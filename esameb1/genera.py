"""Genera il sito statico EsameB1 in esameb1/sito/ a partire da esameb1/dati/.

Uso (dalla radice del repository):
    python3 esameb1/genera.py

Dati: enti.json, sessioni.json (date curate a mano, con fonte), sedi.json (da raccolta/raccogli.py),
citta.json (pagine città). Nessuna dipendenza esterna.
"""
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from decimal import Decimal
from html import escape, unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://esameb1.netlify.app"  # cambiare qui se il nome del sito su Netlify è diverso
NOME = "EsameB1"
ALTRI_SITI = [  # blocco "Altri strumenti utili" in fondo a ogni pagina (URL dal genera.py dell'altro sito)
    ("https://esamidistato.netlify.app/", "EsamiDiStato",
     "date, scadenze e sedi degli esami di Stato per l'abilitazione professionale (ingegnere, psicologo, commercialista, avvocato e altre), prese dalle ordinanze ufficiali."),
    ("https://italy-strikes-today.netlify.app/it/", "Scioperi dei trasporti in Italia oggi e domani",
     "treni, aerei e mezzi pubblici, dal registro ufficiale del Ministero."),
]
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, proprietà https://esameb1.netlify.app

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
import genera_en as EN  # noqa: E402  sezione inglese /en/ (dal 31/10/2026)
import genera_lingue as LG  # noqa: E402  sezioni /uk/ e /ro/ (dal 31/10/2026); hreflang e menu delle lingue per tutto il sito
SITO_ID = "esameb1"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google
AFFILIATI = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8")) if (DATI / "affiliati.json").exists() else {}  # link di affiliazione (dal 30/10/2026: italki)


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_"))


# Frasi Amazon (Programma di Affiliazione Amazon EU): la prima va accanto a ogni link Amazon, la seconda nella privacy.
FRASE_AMAZON = "In qualità di Affiliato Amazon, ricevo un guadagno dagli acquisti idonei."
PRIVACY_AMAZON = ("<h2>Programma di Affiliazione Amazon</h2><p>Partecipiamo al Programma di Affiliazione Amazon EU, un programma di "
                  "affiliazione che permette ai siti di ricevere una commissione pubblicitaria pubblicizzando e fornendo link al sito Amazon.it. "
                  f"{FRASE_AMAZON} I link ad Amazon.it portano a ricerche di libri: prezzi e disponibilità li vedi solo su Amazon e possono cambiare.</p>")


def url_affiliato(voce):
    """URL della voce di dati/affiliati.json ("" se assente); errore se il dominio non è ammesso o se Amazon non ha il tag."""
    url = (AFFILIATI.get(voce) or {}).get("url", "")
    if url and not MON.dominio_ammesso(url):
        raise SystemExit(f"affiliati.json: dominio non ammesso in monetizzazione.json: {url}")
    if url and "amazon." in url and "tag=guideesami-21" not in url:
        raise SystemExit(f"affiliati.json: link Amazon senza tag=guideesami-21: {url}")
    return url


def riquadro_preparati(rel, gratis=None):
    """Riquadro «Preparati alla prova orale» (dal 30/10/2026): insegnante di italiano su italki (voce "italki" di dati/affiliati.json),
    accanto sempre un link gratuito alle prove d'esame ufficiali e, sotto, un link discreto ai libri su Amazon.it (voce "amazon",
    una ricerca con tag=guideesami-21) con la frase obbligatoria di Amazon. Vuoto se nessuna delle due voci ha "url".
    Al massimo uno per pagina; mai nella privacy e nella 404. Nessun prezzo e nessuna promessa di superare l'esame."""
    url = url_affiliato("italki")
    amazon = url_affiliato("amazon")
    if not url and not amazon:
        return ""
    gratis = gratis or f"{rel}esempi/"
    italki_txt = ("\nSu italki scegli tu un insegnante di italiano: fai lezioni 1 a 1 e paghi a lezione." if url else "")
    italki_btn = (f'<a class="btn" href="{escape(url)}" rel="sponsored noopener" target="_blank">{ic("voce")}Trova un insegnante di italiano su italki</a>'
                  if url else "")
    libri = (f'\n<p class="prep-libri">{ic("libro")}<a href="{escape(amazon)}" rel="sponsored noopener" target="_blank">'
             f'Libri per prepararsi all\'esame B1 su Amazon</a></p>\n<p class="small aff-nota">{FRASE_AMAZON}</p>' if amazon else "")
    return f"""<section class="card prep" id="preparati" aria-labelledby="preparati-titolo">
<span class="bolla">{ic("voce")}</span>
<div>
<h2 id="preparati-titolo">Preparati alla prova orale</h2>
<p>La prova orale è la parte che preoccupa molte persone. Per prepararti aiuta parlare spesso con un insegnante madrelingua, anche online.{italki_txt}</p>
<div class="azioni">{italki_btn}<a class="btn btn-2" href="{gratis}">{ic("libro")}Prove d'esame ufficiali gratuite</a></div>{libri}
{MON.nota_trasparenza("it")}
</div>
</section>"""


def riquadro_trasparenza(corpo, lingua="it"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Alcuni link sono di affiliazione: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


OGGI = date.today()

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
PREFETTURA = ("https://prefettura.interno.gov.it/sites/default/files/24/2024-06/"
              "certificato_di_conoscenza_della_lingua_italiana_-ente_privato-.pdf")

# Fonti ufficiali su chi deve fare l'esame e chi è esente (lette il 21/10/2026).
MININT_CITTADINANZA = "https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza"
MININT_DOMANDA = "https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza/cittadinanza-invia-tua-domanda"
PREFETTURA_MILANO = "https://prefettura.interno.gov.it/it/prefetture/milano/cittadinanza"
DLCI_RESIDENZA = ("https://libertaciviliimmigrazione.dlci.interno.gov.it/temi/"
                  "concessione-della-cittadinanza-italiana-residenza-sul-territorio-italiano-ai-sensi-dellart-9")
NORMATTIVA_91 = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1992-02-05;91!vig="  # testo vigente della legge 91/1992 (link usato dal Ministero)

enti = json.loads((DATI / "enti.json").read_text())
sessioni = json.loads((DATI / "sessioni.json").read_text())
sedi = json.loads((DATI / "sedi.json").read_text())
citta = json.loads((DATI / "citta.json").read_text())
esempi = json.loads((DATI / "esempi.json").read_text())  # prove d'esempio ufficiali: solo link e descrizione, con data di verifica
esoneri = json.loads((DATI / "esoneri.json").read_text(encoding="utf-8"))  # chi è esonerato dal B1 (cittadinanza) e dal test A2 (permesso UE), con fonti
RICONG = json.loads((DATI / "ricongiungimento.json").read_text(encoding="utf-8"))  # reddito per il ricongiungimento (assegno sociale dell'anno, da aggiornare ogni gennaio)
ENTE ={e["sigla"]: e for e in enti}
SLUG_ENTE = {"CILS": "cils", "CELI": "celi", "PLIDA": "plida", "CERT.IT": "certit"}
RISULTATI = json.loads((DATI / "risultati.json").read_text(encoding="utf-8"))  # pagine /risultati/<ente>/ (dal 30/10/2026): solo fatti scritti dall'ente, con fonte
SLUG_RISULTATI = {s: r["slug"] for s, r in RISULTATI["enti"].items()}  # cils, celi, plida, cert-it


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
    "voce": '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0M12 17v5M8 22h8"/>',
    "cuffie": '<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3ZM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3Z"/>',
    "archivio": '<rect x="2" y="3" width="20" height="5" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8M10 12h4"/>',
    "matita": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
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
/* prove d'esempio */
.es-vai{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin:18px 0 4px}
.es-vai a{display:grid;gap:4px;background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--brand);border-radius:var(--r);padding:12px 14px;
text-decoration:none;color:var(--ink);font-weight:750;box-shadow:var(--ombra);transition:border-color .15s,background .15s}
.es-vai a:hover{background:var(--brand-soft)}
.es-vai small{font-weight:500;color:var(--ink-3);font-size:.86rem}
.es-vai .ri{display:flex;align-items:center;justify-content:space-between;gap:8px}
.es-vai .ri .i{color:var(--ink-3)}
.es-CILS{border-top-color:var(--cils)!important}.es-CELI{border-top-color:var(--celi)!important}.es-PLIDA{border-top-color:var(--plida)!important}.es-CERTIT{border-top-color:var(--certit)!important}
.es-card{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--brand);border-radius:var(--r-l);padding:20px 22px;box-shadow:var(--ombra);min-width:0;overflow-wrap:anywhere}
.es-card h3:first-child{margin-top:0}
.es-testa{display:flex;flex-wrap:wrap;gap:12px 18px;align-items:center;justify-content:space-between;padding-bottom:16px;margin-bottom:4px;border-bottom:1px solid var(--line)}
.es-testa p{margin:0;color:var(--ink-2);font-size:.95rem;max-width:56ch}
.es-testa .btn{min-height:44px;padding:9px 16px;font-size:.95rem}
.es-prove{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin:12px 0 0;padding:0;list-style:none}
.es-prove li{background:var(--surface-2);border-radius:10px;padding:9px 12px;min-width:0}
.es-prove b{display:block;font-size:.78rem;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3)}
.es-prove span{font-weight:700;font-size:.95rem;font-variant-numeric:tabular-nums}
.es-card>p{color:var(--ink-2);margin:10px 0 0}
.file-lista{list-style:none;padding:0;margin:8px 0 0;display:grid;gap:8px}
.file-lista li{display:grid;grid-template-columns:40px minmax(0,1fr) auto;gap:4px 12px;align-items:center;background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.file-lista .fi{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;background:var(--brand-soft);color:var(--brand)}
.file-lista .fi .i{width:20px;height:20px}
.file-lista a,.file-lista .nome{font-weight:750;display:inline-flex;align-items:center;gap:6px}
.file-lista .cosa{display:block;font-size:.88rem;color:var(--ink-3);line-height:1.4;margin-top:1px}
.file-lista .meta{display:flex;flex-direction:column;align-items:flex-end;gap:2px;font-size:.82rem;color:var(--ink-3);text-align:right;white-space:nowrap}
.file-lista .meta strong{font-size:.78rem;font-weight:800;letter-spacing:.04em;color:var(--ink-2);background:var(--surface-2);padding:1px 7px;border-radius:5px}
.es-tab table{min-width:680px}
.rc-tab table{min-width:640px}
.rc-tab caption{caption-side:top;text-align:left;padding:10px 12px;background:var(--surface)}
@media (max-width:640px){.rc-tab table{min-width:0}.rc-tab thead,.rc-tab .rc-vuota{display:none}
.rc-tab tr{display:grid;grid-template-columns:1fr auto;gap:2px 12px;padding:12px;border-bottom:1px solid var(--line)}
.rc-tab td{display:contents}.rc-tab td:first-child{display:block;grid-column:1/-1;margin-bottom:4px;padding:0;border:0}
.rc-tab td[data-l]::before{content:attr(data-l);color:var(--ink-3);font-size:.88rem}
.rc-tab tbody tr:last-child{border-bottom:0}}
@media (max-width:640px){.es-vai{grid-template-columns:1fr 1fr;gap:8px}.es-vai a{padding:10px 12px;font-size:.95rem}.es-vai small{font-size:.8rem}.es-card{padding:16px}.es-testa .btn{flex:1 1 100%}.file-lista li{grid-template-columns:36px minmax(0,1fr)}.file-lista .fi{width:36px;height:36px}
.file-lista .meta{grid-column:2;flex-direction:row;flex-wrap:wrap;align-items:center;gap:4px 10px;text-align:left;white-space:normal}}
table.conf td.si{color:var(--brand-ink);font-weight:650}
/* tabelle delle pagine risultati: su mobile ogni riga diventa una scheda con le etichette */
.ris-tab table{min-width:680px}
.ris-tab td .eb{margin-right:6px}
.ris-tab .ris-guida{white-space:nowrap}
@media (max-width:640px){.ris-tab table,.ris-tab tbody{display:block;min-width:0}.ris-tab thead{display:none}
.ris-tab tr{display:block;padding:12px 14px;border-bottom:1px solid var(--line)}
.ris-tab table.conf td{display:block;border:0;padding:3px 0}
.ris-tab table.conf td:first-child{padding-bottom:6px}
.ris-tab td[data-l]::before{content:attr(data-l);display:block;color:var(--ink-3);font-size:.8rem;font-weight:650;text-transform:uppercase;letter-spacing:.04em}
.ris-tab tbody tr:last-child{border-bottom:0}}
.ris-sez{margin-top:8px}
.ris-sez>p{max-width:72ch}
.ris-nota{color:var(--ink-2);font-size:.95rem;max-width:72ch}
table.conf td.no{color:var(--ink-3)}
ol.passi li>div p{margin:4px 0 0;color:var(--ink-2);font-size:.95rem}
ol.passi li .fonte{margin-top:6px}
/* riquadro "Preparati alla prova orale" (link di affiliazione + link gratuito) */
/* calcolatore dei redditi e pagine prefettura (31/10/2026) */
.calc{max-width:560px;margin-top:0}
.calc-esito{display:grid;gap:10px;margin-top:16px;max-width:720px}
.calc-esito>div{border:1.5px solid var(--line-2);border-left-width:6px;border-radius:var(--r);padding:12px 14px;background:var(--surface)}
.calc-esito>div.si{border-left-color:var(--brand)}.calc-esito>div.no{border-left-color:var(--rosso)}
.c-tit{font-weight:700}.c-soglia{color:var(--ink-2);font-size:.95rem}.c-esito{font-weight:700}
.calc-esito>div.si .c-esito{color:var(--brand-ink)}.calc-esito>div.no .c-esito{color:var(--rosso)}
.uff{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.uff li{display:flex;gap:10px;align-items:flex-start;overflow-wrap:anywhere}
.uff li .i{color:var(--brand);margin-top:.25em}
.uff b{font-weight:650}
.citaz{border-left:3px solid var(--line-2);padding:2px 0 2px 12px;margin:8px 0;color:var(--ink-2);font-style:italic;overflow-wrap:anywhere}
.locali{display:grid;gap:12px}
main a[href^="mailto:"]{overflow-wrap:anywhere;word-break:break-word}
@media (max-width:640px){.pref-tab tr{display:block;padding:12px}.pref-tab table.conf td,.pref-tab table.conf td:first-child{display:block;border:0;padding:2px 0;margin:0}
.pref-tab td[data-l]::before{display:block;font-size:.8rem;margin-top:6px}}
.pref-tab td{overflow-wrap:anywhere}
.pref-tab td a{white-space:normal}
.prep{display:grid;grid-template-columns:44px minmax(0,1fr);gap:14px 16px;align-items:start;margin:44px 0 8px;border-left:4px solid var(--brand)}
.prep .bolla{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;background:var(--brand-soft);color:var(--brand)}
.prep .bolla .i{width:22px;height:22px}
.prep h2{margin:0 0 6px;font-size:1.25rem}
.prep p{margin:0;color:var(--ink-2);max-width:68ch}
.prep .azioni{margin:16px 0 0}
.prep .aff-nota{margin:12px 0 0;font-size:.84rem;color:var(--ink-3)}
.prep .prep-libri+.aff-nota{margin-top:4px}
.prep .prep-libri{display:flex;align-items:center;gap:8px;margin:14px 0 0;font-size:.95rem}
.prep .prep-libri .i{flex:none;color:var(--ink-3)}
@media (max-width:640px){.prep{grid-template-columns:1fr;gap:10px}.prep .bolla{width:40px;height:40px}}
.piede .dati{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.07);padding:6px 12px;border-radius:999px;font-weight:600;color:#E8F0ED}
@media (max-width:760px){.piede-griglia{grid-template-columns:1fr}}
"""
CSS += LG.CSS_FONT + LG.CSS_MENU  # font per cirillico e ă/ș/ț (solo se la pagina li contiene) e menu delle lingue (31/10/2026)

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
""" + LG.JS_MENU + "\n"


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


# Titoli e description (30/10/2026, per alzare il CTR): al massimo 65 e 155 caratteri, controllati in pagina().
# Le varianti si provano in ordine: vince la prima che ci sta; " | EsameB1" si aggiunge solo se c'è posto.
MARCHIO_TITOLO = " | EsameB1"
MAX_TITOLO, MAX_DESC = 65, 155


def titolo_pagina(*varianti):
    for v in varianti:
        if v and len(v + MARCHIO_TITOLO) <= MAX_TITOLO:
            return v + MARCHIO_TITOLO
        if v and len(v) <= MAX_TITOLO:
            return v
    raise SystemExit(f"nessun titolo entro {MAX_TITOLO} caratteri: {varianti}")


def descrizione_pagina(*varianti):
    for v in varianti:
        if v and len(v) <= MAX_DESC:
            return v
    raise SystemExit(f"nessuna description entro {MAX_DESC} caratteri: {varianti}")


def giorno_mese(iso):
    x = d(iso)
    return f"{x.day} {MESI[x.month - 1]}"


def prossima_di(prossime, sigle=None):
    """La prossima sessione (la lista è già in ordine di data), solo degli enti in sigle se indicati. None se non ce ne sono."""
    return next((s for s in prossime if sigle is None or s["ente"] in sigle), None)


def pagina(percorso, titolo, descrizione, corpo, jsonld=None, base=None):
    """Scrive sito/<percorso> con la struttura comune. base: prefisso dei link ("/" per la 404)."""
    if len(titolo) > MAX_TITOLO or len(descrizione) > MAX_DESC:
        raise SystemExit(f"{percorso}: titolo {len(titolo)}/{MAX_TITOLO} o description {len(descrizione)}/{MAX_DESC} troppo lunghi")
    profondita = percorso.count("/")
    rel = base if base is not None else ("../" * profondita or "./")
    avvisami = "#avvisami" if 'id="avvisami"' in corpo else f"{rel or '/'}#avvisami"
    canonico = URL_SITO + "/" + (percorso[:-10] if percorso.endswith("index.html") else percorso)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    home_href = rel or "./"
    # Lingue (31/10/2026): hreflang reciproci it/en/uk/ro solo se la pagina ha equivalenti (genera_en.COPPIE e genera_lingue.PAGINE);
    # il menu delle lingue porta all'equivalente o, se non c'è, alla home di quella lingua (/en/, /uk/, /ro/).
    alternati = LG.alternati(sys.modules[__name__], "it", percorso)
    radice = rel or "/"
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
<link rel="canonical" href="{canonico}">{alternati}
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{URL_SITO}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{canonico}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B6B4F">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
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
<a href="{rel}#date">Date</a><a href="{rel}#citta">Città</a><a href="{rel}come-funziona/"><span class="lungo">Come funziona</span><span class="corto">Guida</span></a>{LG.menu_lingue(sys.modules[__name__], "it", percorso, radice)}<a class="nav-cta" href="{avvisami}" aria-label="Avvisami">{ic("campana")}<span class="lungo">Avvisami</span></a>
</nav>
</div></header>
<main class="wrap" id="contenuto">
{corpo}{riquadro_trasparenza(corpo)}
</main>
<footer class="piede"><div class="wrap">
<div class="piede-griglia">
<div>
<a class="logo" href="{home_href}">{MARCHIO}<span class="logo-testo">Esame<b>B1</b></span></a>
<ul class="piede-link">
<li><a href="{rel}#date">Date d'esame</a></li><li><a href="{rel}#citta">Sedi per città</a></li><li><a href="{rel}come-funziona/">Come funziona</a></li><li><a href="{rel}costo/">Costo</a></li><li><a href="{rel}risultati/">Risultati</a></li><li><a href="{rel}esenzioni-e-domande/">Orale e domande</a></li><li><a href="{rel}esonero-test-italiano/">Chi è esonerato</a></li><li><a href="{rel}esempi/">Prove d'esempio</a></li><li><a href="{rel}esempi/confronto/">CILS, CELI, PLIDA, CERT.IT a confronto</a></li><li><a href="{rel}cittadinanza/">Domanda di cittadinanza</a></li><li><a href="{rel}reddito-minimo-cittadinanza/">Reddito minimo</a></li>{enti_link}{LG.link_piede_lingue("it", percorso, radice)}<li><a href="{rel}privacy.html">Privacy</a></li>
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
<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(s.get('fonte_pagina') or s['fonte'])}" rel="noopener">elenco ufficiale {escape(s['ente'])}</a></span></div></li>"""


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
    """Nomi con cui le fonti scrivono il capoluogo: nome della pagina e nome della provincia (anche bilingue, es. Bolzano/Bozen).
    Per una città che non è capoluogo ("capoluogo": false in citta.json, es. Busto Arsizio) vale solo il suo nome."""
    if not c.get("capoluogo", True):
        return {norma_luogo(c["nome"])}
    return {norma_luogo(c["nome"])} | {norma_luogo(x) for x in c["provincia"].split("/")}


def nel_capoluogo(s, c):
    return norma_luogo(s["citta"]) in nomi_capoluogo(c)


def nome_provincia(c):
    """Per "in provincia di …": il nome della pagina se coincide con la provincia, altrimenti il nome ufficiale (es. Monza e della Brianza)."""
    return c["nome"] if norma_luogo(c["nome"]) in {norma_luogo(x) for x in c["provincia"].split("/")} else c["provincia"].split("/")[0]


def a_(c):
    """"a Milano", "ad Alba"."""
    return f"{'ad' if c['nome'][0] == 'A' else 'a'} {escape(c['nome'])}"


def sedi_pagina(c):
    """Le sedi che la pagina conta come "sue": tutta la provincia per un capoluogo, il solo comune per le altre città."""
    if not c.get("capoluogo", True):
        return [s for s in sedi if nel_capoluogo(s, c)]
    return [s for s in sedi if s["provincia"] == c["provincia"]]


def sedi_di(c):
    return len(sedi_pagina(c))


def n_sedi(n):
    return f"{n} {'sede' if n == 1 else 'sedi'}"


def principali(n=12):
    """Le città con più sedi, per la griglia in evidenza e i link "altre città"."""
    return sorted(citta, key=lambda c: (-sedi_di(c), c["nome"]))[:n]


# Città vicine (blocco "Sedi nelle città vicine" delle pagine città). Per le città più viste (GoatCounter 21-27/10/2026) a mano,
# con le pagine delle province confinanti, anche di altre regioni; per le altre: il capoluogo (se la pagina è di un comune)
# e le città della stessa regione con più sedi. Gli slug senza pagina vengono saltati.
VICINE = {
    "milano": ["monza", "bergamo", "pavia", "lodi", "varese", "busto-arsizio", "como", "novara", "treviglio"],
    "verona": ["vicenza", "mantova", "brescia", "trento", "rovereto", "padova", "rovigo", "arzignano"],
    "napoli": ["caserta", "salerno", "avellino"],
    "roma": ["viterbo", "frosinone", "l-aquila"],
}


def citta_vicine(c, n=6):
    per_slug = {x["slug"]: x for x in citta}
    if c["slug"] in VICINE:
        return [per_slug[s] for s in VICINE[c["slug"]] if s in per_slug]
    regione = regione_di(c)
    cap = [] if c.get("capoluogo", True) else [x for x in citta if x["provincia"] == c["provincia"] and x.get("capoluogo", True)]
    stesse = sorted((x for x in citta if x is not c and x not in cap and regione and regione_di(x) == regione), key=lambda x: (-sedi_di(x), x["nome"]))
    return (cap + stesse)[:n]


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
VOCI_FATTI = {"costo": ("euro", "Quanto costa"), "durata": ("orologio", "Quanto dura"), "orale": ("voce", "L'orale"), "risultati": ("ok", "Risultati"),
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


def link_guide(rel, salta=None, dopo_b1=True):
    """Griglia delle guide. dopo_b1=False: senza le 2 voci del 31/10/2026 (domanda e reddito), per le pagine esempi ed esonero già revisionate."""
    voci = [("costo/", "euro", "Quanto costa", "i prezzi di ogni ente"),
            ("come-funziona/", "lista", "Come si svolge", "durata, cosa portare, esempi"),
            ("risultati/", "ok", "Risultati", "quando arrivano e dove vederli"),
            ("esenzioni-e-domande/", "voce", "Orale e domande", "com'è l'orale, durata, domande"),
            ("esonero-test-italiano/", "scudo", "Chi è esonerato", "dal B1 e dal test A2, con le fonti"),
            ("esempi/", "libro", "Prove d'esempio", "gratis, ufficiali, ente per ente"),
            ("esempi/confronto/", "lista", "I 4 esami a confronto", "durata, prove, punteggio"),
            ("cittadinanza/", "edificio", "Dopo il B1: la domanda", "prefettura per prefettura"),
            ("reddito-minimo-cittadinanza/", "euro", "Reddito minimo", "cittadinanza e carta di soggiorno")]
    return '<div class="griglia link3">' + "".join(
        f'<a href="{rel}{h}">{ic(i)}<span>{t}<small>{sm}</small></span></a>' for h, i, t, sm in voci
        if h != salta and (dopo_b1 or h not in ("cittadinanza/", "reddito-minimo-cittadinanza/"))) + "</div>"


# Città più cercate (blocco in home): Search Console e GoatCounter fino al 27/10/2026 (Milano 22 visite in una settimana, Verona 12,
# Napoli 9, Roma 8; ricerche "esame b1 italiano per cittadinanza verona/modena/milano", "cpia parma"; prima Prato, Bologna, Torino, Genova).
# Da rivedere con i numeri nuovi: i nomi che non hanno più una pagina vengono saltati.
CITTA_CERCATE = ["milano", "verona", "napoli", "roma", "modena", "parma", "torino", "bologna", "firenze", "prato", "genova", "brescia"]


def citta_cercate():
    per_slug = {c["slug"]: c for c in citta}
    return [per_slug[x] for x in CITTA_CERCATE if x in per_slug]


def testo_semplice(html_testo):
    """Testo di una risposta senza tag HTML, per il JSON-LD FAQPage (stesse parole che si vedono in pagina)."""
    return unescape(re.sub(r"<[^>]+>", "", html_testo))


def faq_jsonld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": testo_semplice(q), "acceptedAnswer": {"@type": "Answer", "text": testo_semplice(a)}} for q, a in faq]}


# ---------------------------------------------------------------- pagine
def home(prossime):
    faq = [  # (domanda, risposta in HTML): visibili in pagina e, senza tag, nel JSON-LD FAQPage
        ("Quale esame devo fare per la cittadinanza?", f'Serve un certificato di italiano almeno di livello B1, rilasciato da un ente riconosciuto. I 4 enti principali, con sedi in tutta Italia, sono CILS (Università per Stranieri di Siena), CELI (Università per Stranieri di Perugia), PLIDA (Società Dante Alighieri) e CERT.IT (Università Roma Tre). Fonte: <a href="{PREFETTURA}" rel="noopener">Prefettura – Ministero dell\'Interno</a>. Il Vademecum del Ministero (2025) elenca anche l\'Università per Stranieri «Dante Alighieri» di Reggio Calabria. Per i casi particolari (titoli di studio italiani, esenzioni) leggi <a href="esonero-test-italiano/">chi è esonerato secondo la legge e il Ministero</a> e chiedi alla Prefettura.'),
        ("Chi è esente dall'esame B1?", 'Secondo le istruzioni del Ministero dell\'Interno, non deve presentare il certificato chi ha firmato l\'accordo di integrazione o ha il permesso di soggiorno UE per soggiornanti di lungo periodo. Dal 2025 (sentenza n. 25 della Corte costituzionale) è esonerato anche chi ha gravi limitazioni nell\'imparare la lingua, certificate da una struttura sanitaria pubblica. La legge (art. 9.1 della legge 91/1992) ammette al posto del certificato anche un titolo di studio di un istituto pubblico o paritario riconosciuto. <a href="esonero-test-italiano/">Chi è esonerato, con le fonti</a>.'),
        (f"Quanto reddito serve per il ricongiungimento familiare nel {RICONG['anno']}?", f"Almeno {euro(tabella_ricongiungimento()[0][1])} l'anno con 1 familiare, più {euro(Decimal(RICONG['assegno_sociale']['annuo']) / 2)} per ogni familiare in più: è l'assegno sociale {RICONG['anno']} dell'INPS aumentato della metà per ogni familiare (art. 29 del Testo unico immigrazione). <a href=\"reddito-ricongiungimento-familiare/\">Tabella per numero di familiari, con le fonti</a>."),
        ('Che differenza c\'è tra "B1 cittadinanza" e B1 normale?', 'CILS e CELI hanno un esame B1 pensato per la cittadinanza, con più sessioni durante l\'anno. Il B1 "normale" degli stessi enti, il PLIDA B1 e il CERT.IT B1 sono anch\'essi certificati di livello B1. Leggi la <a href="come-funziona/">pagina Come funziona</a>.'),
        ("Come mi iscrivo?", "Ci si iscrive presso la sede d'esame, non su questo sito. Scegli una sede nella tua città, contattala e chiedi costo, documenti e scadenza."),
        ("Quanto costa l'esame B1 per la cittadinanza?", "CILS B1 Cittadinanza: 100 €, la stessa tassa in tutta Italia. CERT.IT B1: 80 € alla sede di Roma Tre. CELI e PLIDA: il prezzo lo decide il centro d'esame (per esempio CELI 2 i cittadinanza 90 € all'Università degli Studi di Milano). <a href=\"costo/\">Tutti i costi, con le fonti</a>."),
        ("Quanto dura l'esame?", "Lo scritto dura da 1 ora e 30 minuti (CERT.IT) a 2 ore e 20 minuti (CELI e PLIDA), secondo l'ente. Poi c'è un orale di 10-15 minuti, di solito lo stesso giorno. <a href=\"come-funziona/#durata\">Durata di ogni esame e cosa portare</a>."),
        ("Quando arrivano i risultati e dove li vedo?", "CILS: circa 3 mesi dopo l'esame, online con matricola e data di nascita. CELI: circa 90 giorni lavorativi, online nell'area riservata del CVCL. PLIDA: online nel tuo account PLIDA. CERT.IT: il sito di Roma Tre non lo spiega, chiedi alla sede. <a href=\"risultati/\">Risultati ente per ente</a>: " + ", ".join(f'<a href="risultati/{SLUG_RISULTATI[e]}/">{e}</a>' for e in ENTE) + "."),
        ("Dove trovo esempi gratis dell'esame B1?", "Ogni ente pubblica gratis sul suo sito una prova d'esempio ufficiale, con audio e soluzioni: CILS B1 Cittadinanza, CELI 2 i, PLIDA B1 e CERT.IT B1. <a href=\"esempi/\">Tutte le prove d'esempio, ente per ente</a>."),
        ("Si può fare l'esame online?", "No. L'esame B1 per la cittadinanza si fa in presenza, in una sede d'esame, con un documento d'identità. <a href=\"come-funziona/#online\">Fonti ufficiali</a>."),
    ]
    faq_html = "\n".join(domanda(q, a) for q, a in faq)
    cercate = citta_cercate()
    griglia = "".join(
        f'<a href="citta/{c["slug"]}/">{ic("pin")}<span>{escape(c["nome"])}<small>{sedi_di(c)} {"sede" if sedi_di(c) == 1 else "sedi"}</small></span></a>'
        for c in sorted(principali(), key=lambda c: c["nome"]) if c not in cercate)
    griglia_cercate = "".join(
        f'<a href="citta/{c["slug"]}/">{ic("pin")}<span>{escape(c["nome"])}<small>{n_sedi(sedi_di(c))}</small></span></a>' for c in cercate)
    corpo = f"""<section class="hero">
<span class="occhiello">{ic("scudo")}CILS · CELI · PLIDA · CERT.IT</span>
<h1>Esame di italiano B1 per la cittadinanza: tutte le date 2026 e 2027</h1>
<p class="lead">Date, scadenze e sedi dei 4 enti principali, per chi chiede la cittadinanza italiana per residenza o matrimonio.</p>
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
{riquadro_preparati("")}
<section id="citta">
<h2>{ic("pin")}Sedi per città</h2>
<h3>Città più cercate</h3>
<div class="griglia">{griglia_cercate}</div>
<h3>Altre città con molte sedi</h3>
<div class="griglia">{griglia}</div>
<h3>Tutte le {len(citta)} città, per regione</h3>
{citta_per_regione("")}
<p class="small">La tua città non c'è? Guarda le sedi per regione nelle pagine
{", ".join(f'<a href="ente/{SLUG_ENTE[e]}/">{e}</a>' for e in ENTE)}.</p>
</section>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{faq_html}
<p class="small">Per chiedere la cittadinanza italiana per residenza o matrimonio serve un certificato di italiano di livello B1.
Qui trovi in un solo posto le date, le scadenze e le sedi dei 4 enti principali: CILS, CELI, PLIDA e CERT.IT.</p>
</section>"""
    p = prossime[0]  # main() si ferma se non ci sono sessioni future
    titolo = titolo_pagina(f"Esame B1 cittadinanza {anni(prossime)}: prossima data {giorno_mese(p['data'])}",
                           f"Esame B1 cittadinanza: prossima data {giorno_mese(p['data'])}")
    descr = descrizione_pagina(
        f"Prossimo esame B1 {il(p['data'])}{data_breve(p['data'])} ({p['ente']}). Tutte le date {anni(prossime)} di CILS, CELI, PLIDA e CERT.IT, "
        f"scadenze, costi e {len(sedi)} sedi in Italia.",
        f"Prossimo esame B1 {il(p['data'])}{giorno_mese(p['data'])} ({p['ente']}). Date, scadenze, costi e {len(sedi)} sedi d'esame in Italia.")
    jsonld = jsonld_sessioni(prossime)
    jsonld["@graph"].append(faq_jsonld(faq))
    pagina("index.html", titolo, descr, corpo, jsonld)


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
        dove = f'{n_c} {"sede" if n_c == 1 else "sedi"} {a_(c)}' if n_c else f'{n_q} in provincia'
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


def sezione_dopo_b1(c):
    """Pagina città → la sua Prefettura (il «passo successivo» dopo l'esame): pagina locale se c'è, altrimenti la riga dell'indice."""
    sl = pref_di(c["provincia"])
    if not sl:
        return ""
    nome = PREF[sl]["nome"]
    if ha_pagina_pref(sl):
        pref = f'<a href="../../cittadinanza/{pref_url(sl)}/">{ic("edificio")}<span>Prefettura di {escape(nome)}<small>contatti e cosa scrive sulla cittadinanza</small></span></a>'
    else:
        pref = f'<a href="../../cittadinanza/#{pref_url(sl)}">{ic("edificio")}<span>Prefettura di {escape(nome)}<small>contatti dell\'ufficio cittadinanza</small></span></a>'
    return f"""<section>
<h2 id="domanda-cittadinanza">{ic("edificio")}Dopo il B1: la domanda di cittadinanza</h2>
<p>Con il certificato B1 la domanda si manda online; poi la segue la <strong>Prefettura di {escape(nome)}</strong>. Prima controlla il reddito minimo.</p>
<div class="griglia link3">{pref}<a href="../../reddito-minimo-cittadinanza/">{ic("euro")}<span>Reddito minimo per la cittadinanza<small>soglie ufficiali e calcolatore</small></span></a><a href="../../cittadinanza/#come">{ic("lista")}<span>Come si presenta la domanda<small>online, 250 €, documenti</small></span></a></div>
</section>"""


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
            blocchi.append(f'<h3 id="sedi-{SLUG_ENTE[e]}">{eb(e)} {e} {a_(c)} ({len(lista)})</h3><ul class="sedi">{"".join(scheda_sede(s) for s in lista)}</ul>{tutte}')
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
    capoluogo = c.get("capoluogo", True)
    mie = qui if capoluogo else in_citta  # le sedi che la pagina conta come sue
    enti_qui = [e for e in ENTE if any(s["ente"] == e for s in mie)]
    conteggio = ", ".join(f"{sum(1 for s in mie if s['ente'] == e)} {e}" for e in enti_qui)
    if capoluogo:
        dove = f"{"A" + a_(c)[1:]} e provincia {'c\'è' if len(mie) == 1 else 'ci sono'} <strong>{n_sedi(len(mie))}</strong>"
        in_piu = ""
    else:
        dove = f"{"A" + a_(c)[1:]} {'c\'è' if len(mie) == 1 else 'ci sono'} <strong>{n_sedi(len(mie))}</strong>"
        cap = next((x for x in citta if x["provincia"] == c["provincia"] and x.get("capoluogo", True)), None)
        in_piu = (f" In provincia di {prov} {'ce n\'è un\'altra' if len(in_prov) == 1 else f'ce ne sono altre {len(in_prov)}'}"
                  + (f', vedi anche la pagina di <a href="../{cap["slug"]}/">{escape(cap["nome"])}</a>.' if cap else ".")) if in_prov else ""
    vicine_griglia = "".join(
        f'<a href="../{x["slug"]}/">{ic("pin")}<span>{escape(x["nome"])}<small>{n_sedi(sedi_di(x))}</small></span></a>' for x in citta_vicine(c))
    vicine_titolo = "Sedi nelle città vicine" if c["slug"] in VICINE else f"Sedi in altre città: {escape(regione)}"
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), ("Città", "../../#citta"), (c["nome"], None))}
<h1>Esame B1 per la cittadinanza {a_(c)}: date e sedi {anni(prossime)}</h1>
<p class="lead">{dove} dove puoi fare l'esame di italiano B1 per la cittadinanza ({conteggio}).{in_piu}
Le date d'esame sono le stesse in tutta Italia; la scadenza per iscriversi può cambiare da sede a sede.</p>
{risposta(prossime, "")}
<div class="azioni"><a class="btn" href="#avvisami">{ic("campana")}Avvisami per {escape(c['nome'])}</a><a class="btn btn-2" href="#sedi">{ic("pin")}Vedi {'la sede' if len(mie) == 1 else f'le {len(mie)} sedi'}</a></div>
</section>
{avviso("Contatta la sede prima di iscriverti: ti dice costo, documenti e ultimo giorno per iscriverti.")}
<section>
<h2 id="per-ente">{ic("cal")}Prossime date {a_(c)}, ente per ente</h2>
{per_ente(c, qui, in_citta, prossime)}
</section>
<div class="due">
<section>
<h2 id="date">{ic("lista")}Tutte le prossime date (valide anche {a_(c)})</h2>
{lista_sessioni(prossime)}
</section>
<aside>
{modulo(c['nome'])}
</aside>
</div>
<section>
<h2 id="sedi">{ic("edificio")}Sedi d'esame {a_(c)}</h2>
{"".join(blocchi) or "<p>Nessuna sede trovata nelle fonti ufficiali.</p>"}
{nota_mancano}
{f'<h3 id="vicine">{ic("pin")}{vicine_titolo}</h3><div class="griglia">{vicine_griglia}</div>' if vicine_griglia else ""}
</section>
{riquadro_preparati("../../")}
<section>
<h2>{ic("info")}Prima di iscriverti</h2>
{link_guide("../../", salta="risultati/")}
</section>
<section>
<h2 id="risultati">{ic("ok")}Dopo l'esame: i risultati</h2>
<div class="griglia link3">{"".join(f'<a href="../../risultati/{SLUG_RISULTATI[e]}/">{ic("ok")}<span>Risultati {e}<small>{escape(RISULTATI["enti"][e]["titolo"])}</small></span></a>' for e in enti_qui)}<a href="../../risultati/">{ic("lista")}<span>Tutti gli enti a confronto<small>tempi, punteggio, se non superi</small></span></a></div>
</section>
{sezione_dopo_b1(c)}
<section><h2>{ic("pin")}Altre città</h2>{vicine_html}<div class="altre">{altre}</div></section>"""
    # Titolo con la prossima data degli enti che hanno sedi qui: si aggiorna da solo a ogni rigenerazione (dati/sessioni.json).
    a_c = f"{'ad' if c['nome'][0] == 'A' else 'a'} {c['nome']}"  # come a_(), senza escape: titolo e description li passa escape() in pagina()
    p = prossima_di(prossime, enti_qui)
    dove_d = f"{a_c} e provincia" if capoluogo else a_c
    if p:
        titolo = titolo_pagina(f"Esame B1 cittadinanza {a_c}: prossima data {data_breve(p['data'])}",
                               f"Esame B1 cittadinanza {a_c}: prossima data {giorno_mese(p['data'])}",
                               f"Esame B1 cittadinanza {c['nome']}: prossima data {giorno_mese(p['data'])}",
                               f"B1 cittadinanza {a_c}: prossima data {giorno_mese(p['data'])}",
                               f"Esame B1 cittadinanza {a_c}: date e sedi")
        prossimo_d = f"prossimo esame {il(p['data'])}{giorno_mese(p['data'])} ({p['ente']})"
    else:
        titolo = titolo_pagina(f"Esame B1 cittadinanza {a_c}: date e {n_sedi(len(mie))}", f"Esame B1 cittadinanza {a_c}: date e sedi")
        prossimo_d = "date d'esame"
    quante = f"{n_sedi(len(mie))} {enti_qui[0]}" if len(enti_qui) == 1 else f"{n_sedi(len(mie))} ({conteggio})"
    quali = f"{n_sedi(len(mie))} {enti_qui[0]}" if len(enti_qui) == 1 else f"{n_sedi(len(mie))} ({', '.join(enti_qui)})"
    descr = descrizione_pagina(
        f"Esame di italiano B1 per la cittadinanza {dove_d}: {quante}, {prossimo_d}, scadenze, costi e contatti.",
        f"Esame di italiano B1 per la cittadinanza {dove_d}: {quali}, {prossimo_d}, scadenze e contatti.",
        f"Esame B1 cittadinanza {dove_d}: {quali}, {prossimo_d}, scadenze e contatti delle sedi.",
        f"Esame B1 cittadinanza {dove_d}: {n_sedi(len(mie))}, {prossimo_d}, scadenze e contatti delle sedi.")
    pagina(f"citta/{c['slug']}/index.html", titolo, descr, corpo)


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
    citta_ente = [(c, sum(1 for s in sedi_pagina(c) if s["ente"] == sigla)) for c in sorted(citta, key=lambda c: c["nome"])]
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
<li>{ic("lista")}<a href="{escape(e['pagina_sedi'])}" rel="noopener">elenco ufficiale delle sedi</a></li>
<li>{ic("libro")}<a href="../../esempi/{SLUG_ENTE[sigla]}/">Prove d'esempio {escape(sigla)}</a></li>
<li>{ic("ok")}<a href="../../risultati/{SLUG_RISULTATI[sigla]}/">Risultati {escape(sigla)}</a></li></ul>
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
<p><a href="../../esempi/{SLUG_ENTE[sigla]}/">{ic("libro")} Prove d'esempio {escape(sigla)}: PDF e audio ufficiali, com'è fatto l'esame prova per prova, punteggio per superare</a></p>
<p><a href="../../risultati/{SLUG_RISULTATI[sigla]}/">{ic("ok")} Risultati {escape(sigla)}: dove vederli, quando escono, punteggio e cosa fare se non superi</a></p>
</section>
<section>
<h2 id="sedi">{ic("edificio")}Sedi {escape(sigla)} in Italia ({len(sue)})</h2>
{f'<p class="small" style="margin:0 0 8px">Nelle città con una pagina dedicata (con le date e il modulo Avvisami):</p><div class="altre" style="margin-bottom:18px">{citta_link}</div>' if citta_link else ""}
{blocchi}
</section>"""
    periodo = f" {anni(date_ente)}" if date_ente else ""
    corto = nome_r.split(" (")[0]  # "CERT.IT B1 cittadinanza (Roma Tre)" → "CERT.IT B1 cittadinanza"
    p = prossima_di(date_ente)
    if p:  # titolo con la prossima data dell'ente: si aggiorna da solo a ogni rigenerazione
        titolo = titolo_pagina(*[f"{n}: prossima data {q}{s}" for n, q, s in (
            (nome_r, data_breve(p["data"]), f", {len(sue)} sedi"), (corto, data_breve(p["data"]), f", {len(sue)} sedi"),
            (nome_r, data_breve(p["data"]), ""), (corto, data_breve(p["data"]), ""), (corto, giorno_mese(p["data"]), ""))])
        prossimo = f"Prossimo esame {sigla} B1 {il(p['data'])}{data_breve(p['data'])}: {p['esami'][0]}."
        pc = next((x for x in date_ente if x["tipo"] == "cittadinanza"), None)  # es. CELI: prima il CELI 2, poi il CELI 2 i cittadinanza
        if pc and pc is not p:
            prossimo += f" {pc['esami'][0].replace(' (B1)', '')} {il(pc['data'])}{data_breve(pc['data'])}."
    else:
        titolo = titolo_pagina(f"{nome_r}: date, costo e {len(sue)} sedi", f"{corto}: date, costo e {len(sue)} sedi")
        prossimo = "Nessuna nuova data pubblicata per ora."
    costo_d = "costo deciso dal centro" if breve.startswith("lo decide") else f"costo {breve}" if breve else "costo"
    descr = descrizione_pagina(
        f"{prossimo} Date{periodo}, scadenze, {costo_d}, durata, risultati e le {len(sue)} sedi {sigla} in Italia per regione.",
        f"{prossimo} Date, scadenze, {costo_d}, risultati e {len(sue)} sedi {sigla} per regione.",
        f"{prossimo} Scadenze, {costo_d} e {len(sue)} sedi {sigla} per regione.",
        f"{prossimo} Date, costo e {len(sue)} sedi {sigla} per regione.",
        f"{prossimo} Date{periodo}, scadenze, {costo_d}, risultati e {len(sue)} sedi {sigla} per regione.",
        f"{prossimo} Date, scadenze, costo, risultati e {len(sue)} sedi {sigla} per regione.")
    pagina(f"ente/{SLUG_ENTE[sigla]}/index.html", titolo, descr, corpo, jsonld_sessioni(date_ente) if date_ente else None)


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
Fonte: <a href="{PREFETTURA}" rel="noopener">Prefettura – Ministero dell'Interno</a>. Chi ha firmato l'accordo di integrazione o ha il permesso UE di lungo periodo è esente:
<a href="../esonero-test-italiano/">chi è esonerato, secondo la legge e il Ministero</a>. Per il tuo caso specifico chiedi alla Prefettura: questo sito non dà consulenza.</p>
<h2>{ic("scudo")}I 4 enti principali</h2>
<div class="tab-wrap"><table class="conf"><thead><tr><th>Ente</th><th>Esame per la cittadinanza</th><th>Sedi in Italia</th><th></th></tr></thead>
<tbody>{righe}</tbody></table></div>
<p class="small">Il Vademecum del Ministero dell'Interno (2025) elenca anche un quinto ente, l'Università per Stranieri «Dante Alighieri» di Reggio Calabria: <a href="../esonero-test-italiano/">quali certificati valgono, con le fonti</a>.</p>
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
<p><a href="../esempi/">Le prove d'esempio ente per ente: cosa contengono (PDF, audio, soluzioni), com'è fatta la prova e come esercitarti</a> ·
<a href="../esempi/confronto/">CILS, CELI, PLIDA e CERT.IT a confronto: durata, prove e punteggio</a></p>
{riquadro_preparati("../")}
<h2>{ic("euro")}Costo e risultati</h2>
<p>CILS B1 Cittadinanza costa 100 €, CERT.IT B1 80 € a Roma Tre; per CELI e PLIDA il prezzo lo decide il centro. <a href="../costo/">Tutti i costi</a> ·
<a href="../risultati/">Quando arrivano i risultati</a>.</p>
{modulo()}"""
    pagina("come-funziona/index.html", titolo_pagina("Esame B1 cittadinanza: come funziona, quanto dura, cosa portare"),
           descrizione_pagina(f"Le 4 prove dell'esame B1 per la cittadinanza (ascolto, lettura, scrittura, orale di 10-15 minuti), i {len(enti)} enti "
                              "principali, cosa portare, esempi gratis."), corpo)


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
</div>
{riquadro_preparati("../")}"""
    cils = ENTE["CILS"]["prezzo_eur"]  # tassa ufficiale unica (dati/enti.json, con prezzo_url); CERT.IT: solo alla sede di Roma Tre
    certit = re.match(r"(\d+) €", ENTE["CERT.IT"]["fatti"]["costo"]["breve"]).group(1)
    pagina("costo/index.html", titolo_pagina(f"Quanto costa l'esame B1 cittadinanza? CILS {cils} €, CELI e PLIDA"),
           descrizione_pagina(f"Esame B1 per la cittadinanza: CILS B1 Cittadinanza {cils} € in tutta Italia, CERT.IT B1 {certit} € a Roma Tre, "
                              "CELI e PLIDA a prezzo del centro. Fonti ufficiali."), corpo)


# ---------------------------------------------------------------- risultati (indice + una pagina per ente, dal 30/10/2026)
# Dati in dati/risultati.json: solo fatti scritti dall'ente su pagine o documenti ufficiali, con la data di lettura.
# Se l'ente non scrive un dato (tempi PLIDA e CERT.IT, pagina dei risultati CERT.IT) la pagina lo dice e non dà numeri.
ANNO_RIS = OGGI.year  # l'anno nel titolo: è quello che la gente cerca ("risultati cils b1 cittadinanza 2026")


def con_mail(testo_html):
    """Gli indirizzi email ufficiali citati nel testo (già con escape) diventano link mailto."""
    return re.sub(r"[\w.-]+@[\w-]+(?:\.[\w-]+)*\.it", lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', testo_html)


def fonte_ris(r, chiavi, parola="Fonte"):
    link = " · ".join(f'<a href="{escape(r["fonti"][k]["url"])}" rel="noopener">{escape(r["fonti"][k]["nome"])}</a>' for k in chiavi)
    quando = data_breve(RISULTATI["verificato_il"])
    if parola == "Fonti lette":
        return f'<div class="fonte">{ic("doc")}<span>Fonti lette il {quando}: {link}</span></div>'
    una = len(chiavi) == 1
    return f'<div class="fonte">{ic("doc")}<span>{"Fonte" if una else "Fonti"}: {link} · {"letta" if una else "lette"} il {quando}</span></div>'


def tabella_risultati(rel, colonne):
    """Tabella "risposta rapida" per ente. colonne: "dove" (dove vederli, cosa serve, tempi) o "esito" (punteggio, se non superi)."""
    righe = []
    for e in enti:
        s = e["sigla"]
        r = RISULTATI["enti"][s]
        t = r["tabella"]
        guida = f'<a class="ris-guida" href="{rel}{r["slug"]}/">Risultati {escape(s)} {ic("freccia")}</a>'
        if colonne == "dove":
            tempi = escape(t["tempi"]) if t.get("tempi") else '<span class="small">non scritto dall\'ente</span>'
            celle = (f'<td data-l="Dove vedi il risultato">{escape(t["dove"])}</td><td data-l="Cosa ti serve">{escape(t["serve"])}</td>'
                     f'<td data-l="Quanto tempo (scritto dall\'ente)">{tempi}</td>')
        else:
            celle = f'<td data-l="Per superare">{escape(t["superare"])}</td><td data-l="Se non superi">{escape(t["ripeti"])}</td>'
        righe.append(f'<tr><td>{eb(s)}<strong>{escape(r["esame"])}</strong><br>{guida}</td>{celle}</tr>')
    testa = ('<th scope="col">Ente</th><th scope="col">Dove vedi il risultato</th><th scope="col">Cosa ti serve</th><th scope="col">Quanto tempo (scritto dall\'ente)</th>'
             if colonne == "dove" else '<th scope="col">Ente</th><th scope="col">Per superare</th><th scope="col">Se non superi una parte</th>')
    return f'<div class="tab-wrap ris-tab"><table class="conf"><thead><tr>{testa}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'


def faq_ris(faq):
    jsonld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return jsonld, "".join(domanda(escape(q), con_mail(escape(a))) for q, a in faq)


def pagina_risultati(prossime):
    """Indice: risposta rapida ente per ente in alto (tabella), poi punteggio e cosa fare se non superi, le 4 guide, date e domande."""
    v = data_breve(RISULTATI["verificato_il"])
    R = RISULTATI["enti"]
    fonti = " · ".join(f'<a href="{escape(R[s]["fonti"][R[s]["fonte_risposta"]]["url"])}" rel="noopener">{escape(s)}</a>' for s in ENTE)
    guide = "".join(
        f'<a href="{R[s]["slug"]}/">{ic("ok")}<span>Risultati {escape(R[s]["esame"])}<small>{escape(R[s]["titolo"])}</small></span></a>' for s in ENTE)
    faq = [
        ("Dove vedo i risultati dell'esame B1 per la cittadinanza?",
         "Dipende dall'ente. CILS: online nella pagina «Il mio risultato» dell'Università per Stranieri di Siena, con matricola e data di nascita. "
         "CELI: online nell'area riservata del CVCL di Perugia, con matricola e data di nascita, o al centro d'esame. PLIDA: online su "
         "certificazioneplida.dante.global, con l'email e la password del tuo account. CERT.IT: il sito di Roma Tre non lo spiega, chiedi alla sede."),
        ("Quando escono i risultati dell'esame B1?",
         "CILS: circa 3 mesi dopo l'esame. CELI: circa 90 giorni lavorativi da quando le prove arrivano a Perugia. PLIDA e CERT.IT non scrivono i tempi "
         "nelle pagine ufficiali che abbiamo letto: chiedi al centro d'esame."),
        ("Il risultato arriva il giorno dell'esame?",
         "Per CILS e CELI no. Per il CILS tutte le prove, anche l'orale registrato, sono valutate dal Centro CILS di Siena. Per il CELI lo scritto è corretto "
         "dal CVCL di Perugia e la commissione dell'orale non comunica il punteggio al candidato. PLIDA e CERT.IT non lo scrivono nelle pagine che abbiamo letto."),
        ("Quale punteggio serve per superare l'esame B1?",
         "CILS: la sufficienza in ogni abilità. CELI 2 i cittadinanza: almeno 72 punti su 120 nello scritto, almeno 11 nell'orale e almeno 92 su 160 in tutto. "
         "PLIDA B1: almeno 18 punti su 30 in ogni abilità. CERT.IT B1: il 60% dei punti nello scritto e il 60% nell'orale."),
        ("Se non supero l'esame, devo rifare tutto?",
         "Dipende dall'ente. CILS B1 Cittadinanza: sì, rifai tutto. CELI: entro un anno rifai solo lo scritto o solo l'orale, pagando il 70% della tassa. "
         "PLIDA: entro 18 mesi recuperi solo le abilità non superate (da 1 a 3). CERT.IT: per il B1 il sito non lo dice, chiedi alla sede."),
        ("Il certificato B1 scade?",
         "L'Università per Stranieri di Siena scrive che oggi il certificato CILS non ha scadenza; l'Università per Stranieri di Perugia scrive che i "
         "certificati CELI non hanno scadenza. Per PLIDA e CERT.IT non l'abbiamo trovato scritto nelle pagine lette."),
    ]
    jsonld, faq_html = faq_ris(faq)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Risultati", None))}
<span class="occhiello">{ic("ok")}Fonti ufficiali degli enti · lette il {v}</span>
<h1>Risultati dell'esame B1 per la cittadinanza {ANNO_RIS}: dove vederli, ente per ente</h1>
<p class="lead">CILS e CELI pubblicano il risultato online con numero di matricola e data di nascita (CILS circa 3 mesi dopo l'esame, CELI circa 90 giorni lavorativi dopo l'arrivo delle prove a Perugia),
PLIDA nel tuo account online, mentre il sito CERT.IT non spiega dove vederlo. Fonti: pagine ufficiali {fonti}, lette il {v}.</p>
</section>
<section>
<h2 id="dove">{ic("ok")}Risposta rapida: dove vedi il risultato</h2>
{tabella_risultati("", "dove")}
<p class="small">«Non scritto dall'ente»: l'ente non indica i tempi nelle pagine ufficiali che abbiamo letto. Non scriviamo tempi che l'ente non ha scritto: chiedi al centro dove hai fatto l'esame.</p>
</section>
<section>
<h2 id="punteggio">{ic("lista")}Punteggio per superare e cosa fare se non superi</h2>
{tabella_risultati("", "esito")}
</section>
<section>
<h2 id="guide">{ic("info")}Le guide ente per ente</h2>
<p>Passo per passo dove vedere il risultato, il certificato, il punteggio, cosa fare se non superi, le prossime date e le domande frequenti.</p>
<div class="griglia link3">{guide}</div>
</section>
<div class="due">
<section>
<h2 id="date">{ic("cal")}Devi rifare l'esame? Le prossime date</h2>
{lista_sessioni(prossime[:6], con_filtri=False)}
<p><a href="../#date">Tutte le date</a></p>
</section>
<aside>{modulo()}</aside>
</div>
<section>
<h2 id="domande">{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<h2>{ic("info")}Altre domande</h2>
{link_guide("../", salta="risultati/")}
</section>"""
    pagina("risultati/index.html", titolo_pagina(f"Risultati B1 cittadinanza {ANNO_RIS}: CILS, CELI, PLIDA, CERT.IT"),
           descrizione_pagina("Dove vedere i risultati dell'esame B1 cittadinanza: CILS circa 3 mesi, CELI circa 90 giorni lavorativi, "
                              "PLIDA nel tuo account, CERT.IT dalla sede."), corpo, jsonld)


def pagina_risultati_ente(e, prossime):
    s = e["sigla"]
    r = RISULTATI["enti"][s]
    v = data_breve(RISULTATI["verificato_il"])
    voci = r["voci"]
    f0 = r["fonti"][r["fonte_risposta"]]
    t = r["tabella"]
    bott = r["bottone"]
    # in breve: tre schede
    tempi_b = t["tempi"] if t.get("tempi") else "L'ente non lo scrive"
    breve = (f'<div class="fatti">'
             f'<div class="fatto"><div class="f-et">{ic("web")}<span>Dove</span></div><p>{escape(t["dove"])}</p></div>'
             f'<div class="fatto"><div class="f-et">{ic("orologio")}<span>Quanto tempo</span></div>'
             + (f'<div class="f-breve">{escape(tempi_b)}</div>' if len(tempi_b) <= 28 else f'<p><strong>{escape(tempi_b)}</strong></p>') + '</div>'
             f'<div class="fatto"><div class="f-et">{ic("scudo")}<span>Cosa ti serve</span></div><p>{escape(t["serve"][0].upper() + t["serve"][1:])}.</p></div></div>')
    # dove
    dv = voci["dove"]
    if dv.get("passi"):
        passi = []
        for i, x in enumerate(dv["passi"]):
            extra = f' <a href="{escape(bott["url"])}" rel="noopener">Apri la pagina ufficiale</a>' if i == 0 else ""
            passi.append(f"<li><span>{con_mail(escape(x))}{extra}</span></li>")
        dove_html = f'<ol class="passi">{"".join(passi)}</ol>'
    else:
        dove_html = f'<p>{con_mail(escape(dv["testo"]))}</p>'
    if dv.get("nota"):
        dove_html += f'<p class="ris-nota">{con_mail(escape(dv["nota"]))}</p>'
    nome_ente = escape(e["ente"])

    def sezione(chiave, id_, icona, titolo, vuoto):
        x = voci.get(chiave)
        if not x:
            return ""
        testo = f'<p>{con_mail(escape(x["testo"]))}</p>' if x.get("testo") else f"<p>{vuoto}</p>"
        return f'<section class="ris-sez"><h2 id="{id_}">{ic(icona)}{titolo}</h2>{testo}{fonte_ris(r, x["fonti"], "Fonti lette" if not x.get("testo") else "Fonte")}</section>'

    tempi_vuoto = (f"Nelle pagine ufficiali che abbiamo letto, {escape(s)} ({nome_ente}) non scrive dopo quanto tempo escono i risultati. "
                   "Non diamo tempi che l'ente non ha scritto: chiedi al centro dove hai fatto l'esame.")
    cert_vuoto = f"Il sito ufficiale {escape(s)} non spiega quando e come ricevi il certificato: chiedilo alla sede dove hai fatto l'esame."
    sezioni = "".join([
        sezione("tempi", "quando", "orologio", f"Quando escono i risultati {escape(s)}", tempi_vuoto),
        sezione("lettere", "lettere", "lista", "Come si legge il risultato", ""),
        sezione("certificato", "certificato", "doc", f"Il certificato {escape(s)}", cert_vuoto),
        sezione("punteggio", "punteggio", "ok", "Quale punteggio serve per superare", ""),
        sezione("non_superato", "non-superato", "attenzione", "Se non hai superato l'esame", ""),
        sezione("prove", "prove", "archivio", "Vedere le prove e fare ricorso", ""),
        sezione("chiarimenti", "chiarimenti", "mail", "Domande sul risultato", ""),
    ])
    date_ente = [x for x in prossime if x["ente"] == s]
    date_html = (lista_sessioni(date_ente[:6], con_filtri=False) if date_ente
                 else "<p>Nessuna data futura pubblicata dall'ente per ora. Controlliamo il calendario ufficiale ogni settimana.</p>")
    jsonld, faq_html = faq_ris(r["faq"])
    altri = "".join(f'<a href="../{RISULTATI["enti"][x]["slug"]}/">Risultati {escape(x)}</a>' for x in ENTE if x != s)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), ("Risultati", "../"), (s, None))}
<span class="occhiello">{ic("scudo")}{nome_ente} · fonti lette il {v}</span>
<h1>Risultati {escape(r["esame"])}: {escape(r["titolo"])}</h1>
<p class="lead">{con_mail(escape(r["risposta"]))} Fonte: <a href="{escape(f0["url"])}" rel="noopener">{escape(f0["nome"])}</a>, letta il {v}.</p>
<div class="azioni"><a class="btn" href="{escape(bott["url"])}" rel="noopener">{ic("freccia")}{escape(bott["testo"])}</a><a class="btn btn-2" href="#date">{ic("cal")}Prossime date {escape(s)}</a></div>
</section>
<section class="ris-sez" aria-label="In breve">{breve}</section>
<section class="ris-sez">
<h2 id="dove">{ic("web")}Dove e come vedi il risultato</h2>
{dove_html}
{fonte_ris(r, dv["fonti"])}
</section>
{sezioni}
<div class="due">
<section>
<h2 id="date">{ic("cal")}Prossime date {escape(s)} (livello B1)</h2>
{date_html}
<p><a href="../../ente/{SLUG_ENTE[s]}/">{escape(NOME_RICERCA[s])}: tutte le date, il costo e le sedi</a></p>
</section>
<aside>{modulo()}</aside>
</div>
<section>
<h2 id="domande">{ic("info")}Domande frequenti sui risultati {escape(s)}</h2>
{faq_html}
</section>
<section>
<h2>{ic("ok")}Risultati degli altri enti</h2>
<div class="altre"><a href="../">Tutti gli enti a confronto</a>{altri}</div>
<h2>{ic("info")}Altre domande</h2>
{link_guide("../../")}
</section>"""
    dove_desc = {True: "con email e password", False: "con matricola e data di nascita", None: "chiedendo alla sede"}[t.get("login")]
    tempi_desc = f"Escono {t['tempi']}" if t.get("tempi") else "L'ente non scrive i tempi"
    base_desc = f"Dove vedere i risultati {r['esame']} ({dove_desc}). {tempi_desc}."
    pagina(f"risultati/{r['slug']}/index.html",
           titolo_pagina(f"Risultati {s} B1 cittadinanza {ANNO_RIS}: {r['titolo']}"),
           descrizione_pagina(f"{base_desc} Certificato, punteggio minimo e cosa fare se non superi, con le fonti ufficiali.",
                              f"{base_desc} Certificato, punteggio minimo e cosa fare se non superi.",
                              f"{base_desc} Punteggio minimo e cosa fare se non superi.",
                              f"{base_desc} Punteggio e cosa fare se non superi.", base_desc), corpo, jsonld)


def tabella_prove():
    """Tabella delle 4 prove con i tempi di ogni ente (dati/enti.json → fatti.durata.prove, con le stesse fonti della durata)."""
    colonne = ["ascolto", "lettura", "scrittura", "orale"]
    righe = []
    for e in enti:
        f = e["fatti"]["durata"]
        celle, fatte = [], set()
        for col in colonne:
            if col in fatte:
                continue
            parte = next(p for p in f["prove"]["parti"] if col in p["prove"])
            fatte |= set(parte["prove"])
            celle.append(f'<td{f" colspan=\"{len(parte['prove'])}\"" if len(parte["prove"]) > 1 else ""}>{escape(parte["tempo"])}</td>')
        righe.append(f"<tr><td><strong>{eb(e['sigla'])}</strong><br><span class='small'>{escape(e.get('prezzo_esame') or NOME_RICERCA[e['sigla']])}</span></td>"
                     f"{''.join(celle)}<td><strong>{escape(f['prove']['totale'])}</strong></td></tr>")
    fonti = " · ".join(f'<a href="{escape(x["url"])}" rel="noopener">{escape(e["sigla"])}: {escape(x["nome"])}</a>'
                       for e in enti for x in e["fatti"]["durata"]["fonti"][:1])
    return (f'<div class="tab-wrap"><table class="conf"><thead><tr><th>Esame</th><th>Ascolto</th><th>Lettura</th><th>Scrittura</th><th>Orale</th><th>In tutto</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>'
            f'<div class="fonte">{ic("doc")}<span>Fonti: {fonti} · controllato il {data_breve(max(e["fatti"]["durata"]["verificato_il"] for e in enti))}</span></div>')


def pagina_esenzioni():
    """Esenzioni dall'esame B1 (art. 9.1 legge 91/1992), prove, orale, durata, domande. Ogni affermazione ha la sua fonte ufficiale."""
    fonte_minint = f'<a href="{MININT_DOMANDA}" rel="noopener">Ministero dell\'Interno, «Cittadinanza: invia la tua domanda»</a>'
    fonte_pdf = f'<a href="{PREFETTURA}" rel="noopener">nota della Prefettura sul certificato B1</a>'
    verifica = "controllato il 21 ottobre 2026"

    # Dal 31/10/2026 i casi di esonero, con tutte le fonti, sono nella pagina /esonero-test-italiano/: qui solo il riassunto.
    fonte_esonero = (f'<a href="{escape(esoneri["fonti"]["legge91"]["url"])}" rel="noopener">art. 9.1 della legge 91/1992</a> · '
                     f'<a href="{escape(esoneri["fonti"]["vademecum"]["url"])}" rel="noopener">Vademecum del Ministero dell\'Interno (aprile 2025)</a>')
    esenti = f"""<ul class="cifre" style="flex-direction:column;align-items:flex-start;gap:8px">
<li>{ic("ok")}<span>chi ha firmato l'<strong>accordo di integrazione</strong> (art. 4-bis del Testo unico sull'immigrazione)</span></li>
<li>{ic("ok")}<span>chi ha il <strong>permesso di soggiorno UE per soggiornanti di lungo periodo</strong> (la «carta di soggiorno»)</span></li>
<li>{ic("ok")}<span>chi ha <strong>gravi limitazioni</strong> nell'imparare la lingua per età, malattia o disabilità, con certificato di una struttura sanitaria pubblica (sentenza n. 25/2025 della Corte costituzionale)</span></li>
<li>{ic("doc")}<span>al posto del certificato vale un <strong>titolo di studio</strong> in lingua italiana di una scuola pubblica o paritaria, dalla scuola media in su</span></li>
</ul>
<div class="fonte">{ic("doc")}<span>Fonti: {fonte_esonero} · lette il {data_breve(esoneri["verificato_il"])}</span></div>
<p><a class="btn btn-2" href="../esonero-test-italiano/">{ic("scudo")}Chi è esonerato: tutti i casi, i documenti e le fonti</a></p>"""

    esempi = "".join(
        f'<li><span>{eb(e["sigla"])} <a href="{escape(e["fatti"]["esempi"]["url"])}" rel="noopener">{escape(e["fatti"]["esempi"]["testo"])}</a></span></li>'
        for e in enti)

    faq = [
        ("Chi è esente dall'esame B1 per la cittadinanza?",
         "Secondo la legge e le istruzioni del Ministero dell'Interno, non deve presentare il certificato chi ha firmato l'accordo di integrazione (art. 4-bis del Testo unico "
         "sull'immigrazione) e chi ha il permesso di soggiorno UE per soggiornanti di lungo periodo. Dal 2025 (sentenza n. 25 della Corte costituzionale) è esonerato anche chi ha "
         "gravi limitazioni nell'imparare la lingua, certificate da una struttura sanitaria pubblica. Per tutti gli altri serve un certificato di livello almeno B1 "
         "di un ente riconosciuto, oppure un titolo di studio in italiano di un istituto pubblico o paritario. La Prefettura valuta ogni caso. Tutti i casi sono nella pagina «Chi è esonerato»."),
        ("Ho un diploma o una laurea italiana: devo fare l'esame B1?",
         "Secondo la norma (art. 9.1 della legge 91/1992) al posto del certificato vale un titolo di studio rilasciato da un istituto di istruzione pubblico o "
         "paritario riconosciuto dal Ministero dell'Istruzione e dal Ministero degli Affari Esteri. La Prefettura di Milano indica l'autocertificazione per i titoli "
         "di enti pubblici e la copia autenticata per quelli di istituti paritari o privati. Chiedi conferma alla tua Prefettura prima di inviare la domanda."),
        ("Com'è l'orale dell'esame B1 per la cittadinanza?",
         "Dura da 10 minuti (CILS, CERT.IT) a 15 minuti circa (PLIDA). CILS: breve presentazione personale e dialogo con l'esaminatore. CELI 2 i: presentarsi, "
         "descrivere immagini, domande interculturali e di educazione civica, role play. CERT.IT: intervista, simulazione di ruolo e monologo. "
         "L'orale si fa in presenza; per CILS di solito nel pomeriggio dello stesso giorno dello scritto, per gli altri enti il giorno lo dice la sede."),
        ("Quanto dura l'esame B1 per la cittadinanza?",
         "In tutto da 1 ora e 40 minuti (CERT.IT) a 2 ore e 30 minuti (CELI 2 i cittadinanza). CILS B1 Cittadinanza circa 2 ore, PLIDA B1 circa 2 ore e 35 minuti. "
         "Lo scritto (ascolto, lettura, scrittura) viene prima; per CILS l'orale è di solito nel pomeriggio dello stesso giorno, per gli altri enti chiedi alla sede."),
        ("Quali domande ci sono nell'esame B1?",
         "Non esiste una lista di domande da imparare: le prove cambiano a ogni sessione. Ogni ente pubblica gratis una prova d'esempio ufficiale con audio e "
         "soluzioni; CELI pubblica anche le domande dell'orale. Gli argomenti sono quelli della vita quotidiana: casa, lavoro, servizi, salute, messaggi e email."),
        ("Quando arrivano i risultati?",
         "Dipende dall'ente: CILS circa 3 mesi dopo l'esame, CELI circa 90 giorni lavorativi, PLIDA online nel proprio account. I tempi e dove vederli sono nella pagina Risultati."),
    ]
    jsonld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    faq_html = "".join(domanda(escape(q), escape(a)) for q, a in faq[:-1]) + domanda(
        escape(faq[-1][0]), escape(faq[-1][1]).replace("nella pagina Risultati", 'nella <a href="../risultati/">pagina Risultati</a>'))

    nota_consulenza = ("Questo sito non dà consulenza sulla pratica di cittadinanza. Ogni domanda la valuta la Prefettura: per il tuo caso chiedi lì, "
                       f'oppure leggi la <a href="{MININT_CITTADINANZA}" rel="noopener">pagina del Ministero dell\'Interno</a>.')
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Orale e domande", None))}
<span class="occhiello">{ic("scudo")}Con le fonti ufficiali</span>
<h1>Esame B1 per la cittadinanza: com'è l'orale, quanto dura, che domande ci sono (e chi è esente)</h1>
<p class="lead">Secondo i documenti ufficiali di CILS, CELI, PLIDA, CERT.IT e del Ministero dell'Interno (letti l'ultima volta il {data_breve(max([esoneri["verificato_il"]] + [e["fatti"]["durata"]["verificato_il"] for e in enti]))}): com'è fatto l'esame, com'è l'orale ente per ente, quanto dura e dove vedere domande vere. In breve anche chi è esente. Accanto a ogni risposta c'è la fonte ufficiale.</p>
</section>
{avviso(nota_consulenza)}
<div class="due">
<section>
<h2 id="esenzioni">{ic("scudo")}Chi è esente dall'esame B1, in breve</h2>
<p>Dal 4 dicembre 2018 chi chiede la cittadinanza per residenza o per matrimonio deve avere una conoscenza dell'italiano almeno di livello B1.
Lo dice l'<strong>art. 9.1 della legge 91/1992</strong>, inserito dal decreto-legge 113/2018 (il «decreto sicurezza»), convertito dalla legge 132/2018.
Non deve presentare il certificato:</p>
{esenti}
<h3>Tutti gli altri: serve il certificato</h3>
<p>Chi non rientra nei casi sopra deve allegare alla domanda un certificato di livello almeno B1 di un ente riconosciuto: CILS, CELI, PLIDA, CERT.IT (i 4 enti principali) o l'Università per Stranieri «Dante Alighieri» di Reggio Calabria, che il Vademecum del Ministero elenca come quinto ente.
La nota della Prefettura aggiunge che la certificazione si può conseguire anche presso i CPIA (Centri provinciali per l'istruzione degli adulti): molti CPIA sono sedi d'esame degli enti,
li trovi nell'<a href="../#citta">elenco per città</a>.</p>
<div class="fonte">{ic("doc")}<span>Fonti: {fonte_pdf} · {fonte_minint} · <a href="{DLCI_RESIDENZA}" rel="noopener">Dipartimento per le libertà civili, cittadinanza per residenza</a> ·
<a href="{NORMATTIVA_91}" rel="noopener">testo della legge 91/1992 su Normattiva</a> · {verifica}</span></div>
</section>
<aside>{modulo()}</aside>
</div>
<section>
<h2 id="prove">{ic("lista")}Com'è fatto l'esame: le 4 prove</h2>
<p>Tutti e quattro gli esami hanno le stesse prove: <strong>ascolto, lettura, scrittura e orale</strong>. Cambiano i tempi e il modo di contare i punti.</p>
{tabella_prove()}
</section>
<section>
<h2 id="orale">{ic("voce")}L'orale: come funziona</h2>
<p>L'orale si fa in presenza, con un esaminatore. Ecco cosa chiede ogni ente e quanto dura.</p>
{schede_per_ente("orale")}
</section>
<section>
<h2 id="durata">{ic("orologio")}Quanto dura l'esame</h2>
<p>Lo scritto dura da 1 ora e 30 minuti (CERT.IT) a 2 ore e 20 minuti (CELI e PLIDA); poi c'è l'orale di 10-15 minuti. I tempi di ogni prova sono nella tabella sopra;
cosa portare il giorno dell'esame è in <a href="../come-funziona/#durata">Come funziona</a>.</p>
</section>
<section>
<h2 id="domande">{ic("libro")}Le domande dell'esame: dove vedere esempi veri</h2>
<p>Non esiste una lista di domande da imparare a memoria: le prove cambiano a ogni sessione. Il modo migliore per capire com'è l'esame è la prova d'esempio ufficiale, gratis:</p>
<ul class="cifre" style="flex-direction:column;align-items:flex-start;gap:10px">{esempi}</ul>
<p class="small">Gli argomenti sono quelli della vita di ogni giorno: casa, lavoro, servizi, salute, messaggi ed email. <a href="../esempi/">Tutte le prove d'esempio, ente per ente, con cosa contengono</a> ·
<a href="../esempi/confronto/">i 4 esami a confronto</a>.</p>
</section>
<section>
<h2>{ic("info")}Risultati, costo, come iscriversi</h2>
{link_guide("../", salta="esenzioni-e-domande/")}
</section>
<section>
<h2 id="ricongiungimento">{ic("euro")}Ricongiungimento familiare: quanto reddito serve</h2>
<p>Vuoi far venire in Italia moglie, marito, figli o genitori? Per il nulla osta serve un reddito minimo che dipende dal numero di familiari:
nel {RICONG['anno']} almeno {euro(tabella_ricongiungimento()[0][1])} l'anno con 1 familiare. <a href="../reddito-ricongiungimento-familiare/">Tabella {RICONG['anno']} del reddito per il ricongiungimento familiare, con le fonti</a>.</p>
</section>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{faq_html}
</section>"""
    pagina("esenzioni-e-domande/index.html",
           titolo_pagina("Esame B1 cittadinanza: orale, durata, domande ed esenzioni"),
           descrizione_pagina("Esame B1 per la cittadinanza: com'è l'orale di CILS, CELI, PLIDA e CERT.IT, quanto dura ogni prova, che domande ci sono "
                              "e, in breve, chi è esente."), corpo, jsonld)


# ---------------------------------------------------------------- prove d'esempio: indice /esempi/, una pagina per ente, confronto (dal 31/10/2026)
# Dati in dati/esempi.json (file ufficiali, struttura dell'esame, consigli, domande frequenti, frasi citate) e, per punteggio e
# recupero, dati/risultati.json. Controllo ripetibile dei link e delle frasi citate: raccolta/esempi.py. I file restano sui siti
# degli enti: solo link (CERT.IT nemmeno quelli: note legali di Roma Tre sul deep linking). /esempi-esame-b1/ → /esempi/ (301).
ICONA_FILE = {"PDF": "doc", "MP3": "cuffie", "ZIP": "archivio"}
ES = {e["sigla"]: e for e in esempi["enti"]}
TITOLI_ESEMPI = {  # (titolo della pagina, h1): parole cercate su Google il 31/10/2026 ("cils b1 cittadinanza pdf", "celi b1 cittadinanza esempio"...)
    "CILS": ("CILS B1 Cittadinanza: prove d'esame PDF, audio e chiavi",
             "CILS B1 Cittadinanza: l'esempio d'esame ufficiale, PDF e audio"),
    "CELI": ("Esempio esame CELI B1 cittadinanza (CELI 2 i): PDF, audio, orale",
             "CELI 2 i cittadinanza (B1): gli esempi d'esame ufficiali, PDF, audio e orale"),
    "PLIDA": ("PLIDA B1 esempio: prova d'esame PDF, audio e soluzioni",
              "PLIDA B1: la prova d'esempio ufficiale, PDF, audio e soluzioni"),
    "CERT.IT": ("CERT.IT B1 esempio d'esame: com'è fatto, PDF e audio ufficiali",
                "CERT.IT B1: l'esempio d'esame ufficiale e com'è fatto l'esame"),
}


def peso(byte):
    """Dimensione in unità decimali, alla maniera italiana: 168 KB, 39,5 MB."""
    if byte < 1_000_000:
        return f"{round(byte / 1000)} KB"
    return f"{byte / 1_000_000:.1f} MB".replace(".", ",")


def host(url):
    return re.sub(r"^https?://(www\.)?([^/]+).*$", r"\2", url)


def link_fonti(lista):
    return " · ".join(f'<a href="{escape(x["url"])}" rel="noopener">{escape(x["nome"])}</a>' for x in lista)


def riga_file(f):
    """Una riga dell'elenco dei file. Senza "url" (ente che non vuole link diretti ai file): solo il nome, niente link."""
    dim = (f'{f["numero"]} × ' if f.get("numero") else "") + peso(f["byte"])
    dettagli = [escape(dim)] + ([f'{f["pagine"]} pag.'] if f.get("pagine") else []) + [escape(f["data"])]
    nome = (f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["nome"])}</a>' if f.get("url")
            else f'<span class="nome">{escape(f["nome"])}</span>')
    return (f'<li><span class="fi">{ic(ICONA_FILE[f["formato"]])}</span>'
            f'<div>{nome}<span class="cosa">{escape(f["contenuto"][0].upper() + f["contenuto"][1:])}.</span></div>'
            f'<div class="meta"><strong>{f["formato"]}</strong><span>{" · ".join(dettagli)}</span></div></li>')


def blocco_file(e):
    """I file ufficiali di un ente (link diretti) o, per CERT.IT, cosa trovi sulla pagina ufficiale (senza link ai file)."""
    v = data_breve(esempi["verificato_il"])
    n = len(e["file"])
    if e.get("link_diretti", True):
        host_file = " o ".join(escape(h) for h in dict.fromkeys(host(f["url"]) for f in e["file"]))
        nota = f"Ogni link apre il file sul sito {host_file}. Data: ultima modifica del file sul server dell'ente, o data scritta nel file."
        controllo = f"Link controllati il {v}: i {n} file si aprono tutti (stato 200), con il formato e la dimensione indicati."
    else:
        nota = escape(e["senza_link_diretti"])
        controllo = f"Pagina e file controllati il {v}: si aprono (stato 200), con il formato e la dimensione indicati."
    return (f'<p class="small" style="margin:0">{nota}</p><ul class="file-lista">{"".join(riga_file(f) for f in e["file"])}</ul>'
            f'<div class="fonte">{ic("ok")}<span>{controllo}</span></div>')


def tabella_struttura(e):
    """Prova per prova: cosa devi fare, tempo, punti (dati/esempi.json → prove). Su mobile ogni riga diventa una scheda."""
    righe = "".join(
        f'<tr><td><strong>{escape(p["nome"])}</strong></td><td data-l="Cosa devi fare">{escape(p["cosa"])}</td>'
        f'<td data-l="Tempo">{escape(p["tempo"])}</td><td data-l="Punti">{escape(p["punti"])}</td></tr>' for p in e["prove"])
    return ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Prova</th><th scope="col">Cosa devi fare</th>'
            f'<th scope="col">Tempo</th><th scope="col">Punti</th></tr></thead><tbody>{righe}</tbody></table></div>')


def fonte_risultati(s, chiave):
    """Fonte di una voce di dati/risultati.json (punteggio, non_superato), con la data di lettura."""
    r = RISULTATI["enti"][s]
    lista = [r["fonti"][k] for k in r["voci"][chiave]["fonti"]]
    return f'<div class="fonte">{ic("doc")}<span>{"Fonte" if len(lista) == 1 else "Fonti"}: {link_fonti(lista)} · {"letta" if len(lista) == 1 else "lette"} il {data_breve(RISULTATI["verificato_il"])}</span></div>'


def date_ente_html(prossime, s, rel):
    date_e = [x for x in prossime if x["ente"] == s]
    corpo = (lista_sessioni(date_e[:6], con_filtri=False) if date_e
             else "<p>Nessuna data futura pubblicata dall'ente per ora. Controlliamo il calendario ufficiale ogni settimana.</p>")
    return corpo + f'<p><a href="{rel}ente/{SLUG_ENTE[s]}/">{escape(NOME_RICERCA[s])}: tutte le date, il costo e le sedi</a></p>'


def faq_html_e_jsonld(faq):
    jsonld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return jsonld, "".join(domanda(escape(q), escape(a)) for q, a in faq)


def pagina_esempi(prossime):
    """Indice /esempi/: cosa pubblica ogni ente, durata e punteggio in breve, come esercitarti, condizioni d'uso, domande."""
    v = data_breve(esempi["verificato_il"])
    vai = "".join(
        f'<a class="es-{e["sigla"].replace(".", "")}" id="{SLUG_ENTE[e["sigla"]]}" href="{SLUG_ENTE[e["sigla"]]}/"><span class="ri">{eb(e["sigla"])}{ic("freccia")}</span>'
        f'<span>{escape(e["esame"])}</span><small>{f"{len(e['file'])} file" if e.get("link_diretti", True) else "dalla pagina ufficiale"} · '
        f'{escape(e["materiali"]["audio"])}</small></a>' for e in esempi["enti"])

    def cella(x):
        return f'<td class="{"no" if x.startswith("no") else "si"}">{escape(x)}</td>'
    righe = "".join(
        f'<tr><td>{eb(e["sigla"])}<br><a href="{SLUG_ENTE[e["sigla"]]}/">{escape(e["esame"])}</a></td>'
        + "".join(cella(e["materiali"][k]) for k in ("audio", "soluzioni", "trascrizioni", "orale"))
        + f'<td>{escape(e["aggiornato"])}</td></tr>' for e in esempi["enti"])
    tabella = (f'<div class="tab-wrap es-tab"><table class="conf"><thead><tr><th>Esame</th><th>Audio</th><th>Soluzioni</th><th>Trascrizione dell\'audio</th>'
               f'<th>Orale</th><th>File del</th></tr></thead><tbody>{righe}</tbody></table></div>')
    breve = "".join(
        f'<tr><td>{eb(s)}<strong>{escape(ES[s]["esame"])}</strong><br><a class="ris-guida" href="{SLUG_ENTE[s]}/">Esempio e prove {escape(s)} {ic("freccia")}</a></td>'
        f'<td data-l="Quanto dura">{escape(ENTE[s]["fatti"]["durata"]["prove"]["totale"])}</td>'
        f'<td data-l="Per superare">{escape(RISULTATI["enti"][s]["tabella"]["superare"])}</td>'
        f'<td data-l="Se non superi una parte">{escape(RISULTATI["enti"][s]["tabella"]["ripeti"])}</td></tr>' for s in ENTE)
    tab_breve = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Esame</th><th scope="col">Quanto dura</th>'
                 f'<th scope="col">Per superare</th><th scope="col">Se non superi una parte</th></tr></thead><tbody>{breve}</tbody></table></div>')

    # Consigli presi dai documenti ufficiali degli enti (ognuno con la sua fonte).
    cils_svolg = "https://cils.unistrasi.it/1/94/28/Come_si_svolgono_gli_esami_CILS.htm"
    quaderno_plida = ES["PLIDA"]["fonti_prova"][0]
    certit_pag = ES["CERT.IT"]["fonti_prova"][0]
    consigli = [
        ("Fai la prova intera, con i tempi veri e nell'ordine dell'esame",
         "All'esame CILS si comincia con l'ascolto, poi la lettura, poi la scrittura; l'orale è di solito nel pomeriggio. "
         "PLIDA scrive il tempo all'inizio di ogni prova e non permette appunti, dizionari, libri né telefono: allenati allo stesso modo.",
         [{"nome": "CILS, come si svolgono gli esami", "url": cils_svolg}, quaderno_plida]),
        ("Ascolta ogni audio due volte, non di più",
         "Nel CILS B1 Cittadinanza ogni testo dell'ascolto si sente due volte; nel CERT.IT B1 lo dicono le consegne delle prove di ascolto 1 e 2. "
         "Dopo la prova controlla con la trascrizione (CILS, CELI e PLIDA la pubblicano) le parti che non hai capito.",
         [ES["CILS"]["fonti_prova"][0], certit_pag]),
        ("Segna le risposte sul foglio delle risposte, con la penna giusta",
         "Stampa il foglio delle risposte ufficiale. CILS accetta solo la penna nera; PLIDA chiede una penna non cancellabile blu o nera, niente matita né bianchetto, "
         "e dà 10 minuti alla fine per copiare le risposte sul foglio. Poi correggi con le chiavi.",
         [{"nome": "CILS, come si svolgono gli esami", "url": cils_svolg}, quaderno_plida]),
        ("Nella scrittura conta le parole e rileggi con i criteri ufficiali",
         "Ogni ente chiede un numero preciso di parole: CILS un'email di 80-120, CELI 40-50 e 80-90, PLIDA 110-150 e 70-100, CERT.IT testi brevi (50-80 parole negli esempi della pagina B1). "
         "I criteri di valutazione dicono cosa conta: per CILS efficacia comunicativa, correttezza, lessico, ortografia. PLIDA pubblica anche una prova di scrittura commentata.",
         [{"nome": "criteri di valutazione CILS (PDF)", "url": ES["CILS"]["fonti_prova"][1]["url"]}, ES["CELI"]["fonti_prova"][0], quaderno_plida, certit_pag]),
        ("Prepara l'orale ad alta voce, cominciando da te",
         "Tutti e quattro gli orali cominciano con una presentazione: CILS circa 1 minuto partendo da una lista di domande, PLIDA circa 2 minuti (non valutati) sui tuoi progetti di studio o lavoro, "
         "CELI e CERT.IT con domande su di te. "
         "Poi esercitati sulle tracce ufficiali: le immagini e le domande dell'input orale CELI, la prova del candidato PLIDA (3 minuti di preparazione, con appunti), il «Parlato» CERT.IT.",
         [ES["CILS"]["fonti_prova"][0], quaderno_plida, ES["CELI"]["fonti_prova"][0], {"nome": "input orale CELI 2 i (PDF)", "url": ES["CELI"]["file"][2]["url"]}, certit_pag]),
    ]
    passi = "".join(
        f'<li><div><strong>{t}</strong><p>{escape(x)}</p><div class="fonte">{ic("doc")}<span>Fonte: {link_fonti(f)}</span></div></div></li>'
        for t, x, f in consigli)
    uso = "".join(f'<li><span><strong>{escape(u["ente"])}</strong>: {escape(u["testo"])} (<a href="{escape(u["url"])}" rel="noopener">fonte</a>).</span></li>' for u in esempi["uso"])

    faq = [
        ("Dove trovo gli esempi ufficiali dell'esame B1 per la cittadinanza?",
         "Ogni ente li pubblica gratis sul suo sito: CILS (Università per Stranieri di Siena) alla pagina «Prove Liv. B1 c», CELI (Università per Stranieri di Perugia) alla pagina «Esami CELI immigrati», "
         "PLIDA (Società Dante Alighieri) alla pagina «Preparati all'esame», CERT.IT (Università Roma Tre) in fondo alla pagina «Livello B1». Si scaricano senza registrazione (controllato il " + v + ")."),
        ("C'è una simulazione dell'esame B1 per la cittadinanza?",
         "Gli enti pubblicano prove d'esempio complete, con audio e soluzioni: stampale e falle con i tempi veri, è la simulazione più vicina all'esame. "
         "Nelle pagine ufficiali che abbiamo controllato il " + v + " non c'è un test interattivo online. "
         "Il CERT.IT B1 a Roma Tre si fa al computer (nei centri convenzionati chiedi alla sede), ma sempre in sede."),
        ("L'esame B1 per la cittadinanza è difficile?",
         "Dipende da quanto sei preparato. Il livello B1 chiede di capire i punti principali di testi chiari sulla vita di tutti i giorni e di farsi capire: il sillabo CILS parla di "
         "una produzione «comunicativamente efficace, anche se contiene errori». Per superarlo servono il 60% dei punti nello scritto e nell'orale del CERT.IT, almeno 18 su 30 in ogni abilità "
         "del PLIDA, almeno 72 su 120 nello scritto del CELI 2 i, più un minimo nell'orale. Per capire il tuo livello fai una prova d'esempio ufficiale e correggila con le chiavi."),
        ("Le prove d'esempio hanno le soluzioni e l'audio?",
         "Sì, tutte e quattro. CILS: chiavi, MP3 e trascrizione. CELI: chiavi, MP3 e trascrizione dentro i due zip. PLIDA: soluzioni, trascrizioni e MP3 nello zip. "
         "CERT.IT: chiavi e 3 file MP3; nei file pubblicati non c'è la trascrizione dell'audio."),
        ("Le domande dell'esame sono le stesse degli esempi?",
         "No. Le prove cambiano a ogni sessione: gli esempi servono a capire com'è fatto l'esame (tipo di domande, tempi, punti), non a imparare le risposte a memoria."),
    ]
    jsonld, faq_html = faq_html_e_jsonld(faq)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Prove d'esempio", None))}
<span class="occhiello">{ic("libro")}Fonti ufficiali · controllato il {v}</span>
<h1>Esempi d'esame B1 per la cittadinanza: le prove ufficiali gratis, PDF e audio</h1>
<p class="lead">Secondo le pagine ufficiali dei 4 enti, controllate il {v}, CILS, CELI, PLIDA e CERT.IT pubblicano gratis una prova d'esempio del B1 con audio e soluzioni.
Scegli l'ente: per ognuno trovi i link ai file ufficiali (per CERT.IT la pagina dell'ente), com'è fatta ogni prova, quanto dura e quanti punti servono.</p>
<nav class="es-vai" aria-label="Esempi ente per ente">{vai}</nav>
</section>
{avviso("I file sono degli enti e restano sui loro siti: qui ci sono solo i link e una descrizione. Sono protetti dal diritto d'autore: scaricali per studiare, ma non ricaricarli su altri siti. <a href=\"#uso\">Le condizioni d'uso</a>.")}
<section>
<h2 id="confronto">{ic("lista")}Cosa trovi negli esempi, ente per ente</h2>
{tabella}
</section>
<section>
<h2 id="durata">{ic("orologio")}Durata e punteggio, in breve</h2>
<p>Tutti e quattro gli esami hanno ascolto, lettura, scrittura e orale. Cambiano i tempi, il modo di contare i punti e cosa succede se non superi una parte.</p>
{tab_breve}
<p><a href="confronto/">{ic("lista")} I 4 esami a confronto, prova per prova: tipo di domande, parole da scrivere, orale</a></p>
<div class="fonte">{ic("doc")}<span>Fonti: i documenti ufficiali citati in ogni pagina ente · durata da sillabi e descrizioni (somma dei tempi delle prove, se l'ente non dà il totale) · punteggi letti il {data_breve(RISULTATI["verificato_il"])}</span></div>
</section>
<div class="due">
<section>
<h2 id="esercitarti">{ic("ok")}Come esercitarti</h2>
<p>Cinque consigli presi dai documenti ufficiali degli enti.</p>
<ol class="passi">{passi}</ol>
</section>
<aside>{modulo()}</aside>
</div>
{riquadro_preparati("../", gratis="#confronto")}
<section>
<h2 id="esonero">{ic("scudo")}Devi davvero fare l'esame?</h2>
<p>Non tutti devono presentare il certificato B1 per la cittadinanza: per esempio chi ha il permesso di soggiorno UE per soggiornanti di lungo periodo o ha firmato l'accordo di integrazione.
<a href="../esonero-test-italiano/">Chi è esonerato dal B1 e dal test A2 per la carta di soggiorno, con le fonti</a>.</p>
</section>
<section>
<h2 id="uso">{ic("scudo")}Condizioni d'uso dei materiali</h2>
<p>Le prove d'esempio si scaricano gratis dai siti degli enti per prepararsi all'esame, ma non sono materiali liberi:</p>
<ul>{uso}<li><span><strong>CELI</strong>: sul sito del CVCL non abbiamo trovato una nota specifica; valgono le regole generali del diritto d'autore.</span></li></ul>
<p>Se sei un insegnante e vuoi usarle in classe, condividi il link alla pagina ufficiale; per altri usi chiedi all'ente.</p>
<div class="fonte">{ic("doc")}<span>Note lette il 26 ottobre 2026.</span></div>
</section>
<section>
<h2 id="domande">{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<h2>{ic("info")}Altre domande</h2>
{link_guide("../", salta="esempi/", dopo_b1=False)}
</section>"""
    pagina("esempi/index.html",
           titolo_pagina("Esempi esame B1 cittadinanza: prove ufficiali PDF e audio, 4 enti"),
           descrizione_pagina("Prove d'esempio ufficiali e gratuite dell'esame B1 per la cittadinanza (CILS, CELI 2 i, PLIDA, CERT.IT) con PDF, audio e "
                              "soluzioni. Durata e punteggio."), corpo, jsonld)


def pagina_esempi_ente(e, prossime):
    """/esempi/<ente>/: file ufficiali, struttura prova per prova, punteggio per superare, recupero, come usare l'esempio, date, domande."""
    s = e["sigla"]
    sl = SLUG_ENTE[s]
    v = data_breve(esempi["verificato_il"])
    en = ENTE[s]
    t = RISULTATI["enti"][s]["tabella"]
    voci = RISULTATI["enti"][s]["voci"]
    totale = en["fatti"]["durata"]["prove"]["totale"]
    nome_pagina = e["pagina"]["nome"].split(", ")[0]
    formati = sorted({f["formato"] for f in e["file"]}, key=["PDF", "MP3", "ZIP"].index)
    if e.get("link_diretti", True):
        prima = (f"Secondo la pagina ufficiale «{escape(nome_pagina)}» ({escape(en['ente'])}), controllata il {v}, l'esempio d'esame del {escape(e['esame'])} "
                 f"è gratis e si scarica senza registrazione: {len(e['file'])} file ({', '.join(formati)}).")
    else:
        prima = (f"Secondo la pagina ufficiale «{escape(nome_pagina)}» ({escape(en['ente'])}), controllata il {v}, l'esempio d'esame del {escape(e['esame'])} "
                 "è gratis e si scarica in fondo a quella pagina: uno zip con 4 PDF e 3 file audio.")
    breve = (f'<div class="fatti">'
             f'<div class="fatto"><div class="f-et">{ic("orologio")}<span>Quanto dura</span></div><p><strong>{escape(totale[0].upper() + totale[1:])}</strong></p></div>'
             f'<div class="fatto"><div class="f-et">{ic("ok")}<span>Per superare</span></div><p>{escape(t["superare"][0].upper() + t["superare"][1:])}</p></div>'
             f'<div class="fatto"><div class="f-et">{ic("attenzione")}<span>Se non superi una parte</span></div><p>{escape(t["ripeti"])}</p></div></div>')
    passi = "".join(
        f'<li><div><strong>{escape(c["t"])}</strong><p>{escape(c["x"])}</p><div class="fonte">{ic("doc")}<span>Fonte: {link_fonti(c["fonti"])}</span></div></div></li>'
        for c in e["come_usare"])
    jsonld, faq_html = faq_html_e_jsonld(e["faq"])
    altri = "".join(f'<a href="../{SLUG_ENTE[x]}/">Esempio {escape(x)}</a>' for x in ENTE if x != s)
    titolo_file = "I file ufficiali" if e.get("link_diretti", True) else "Cosa trovi sulla pagina ufficiale"
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), ("Prove d'esempio", "../"), (s, None))}
<span class="occhiello">{ic("libro")}{escape(en["ente"])} · controllato il {v}</span>
<h1>{escape(TITOLI_ESEMPI[s][1])}</h1>
<p class="lead">{prima} Qui sotto trovi cosa c'è nei file, com'è fatto l'esame prova per prova e quanti punti servono per superarlo.</p>
<div class="azioni"><a class="btn" href="{escape(e["pagina"]["url"])}" rel="noopener">{ic("freccia")}Pagina ufficiale {escape(s)}</a><a class="btn btn-2" href="#file">{ic("archivio")}{titolo_file}</a></div>
</section>
<section class="ris-sez" aria-label="In breve">{breve}</section>
<section>
<h2 id="file">{ic("archivio")}{titolo_file}</h2>
<div class="es-card es-{s.replace(".", "")}">{blocco_file(e)}</div>
</section>
<section>
<h2 id="prove">{ic("lista")}Com'è fatto l'esame {escape(e["esame"])}, prova per prova</h2>
{tabella_struttura(e)}
<p class="ris-nota">{escape(e["nota_prove"])} In tutto: {escape(totale)}.</p>
<div class="fonte">{ic("doc")}<span>{"Fonte" if len(e["fonti_struttura"]) == 1 else "Fonti"}: {link_fonti(e["fonti_struttura"])} · controllato il {v}</span></div>
</section>
<section class="ris-sez">
<h2 id="punteggio">{ic("ok")}Quanti punti servono per superare</h2>
<p>{con_mail(escape(voci["punteggio"]["testo"]))}</p>
{fonte_risultati(s, "punteggio")}
</section>
<section class="ris-sez">
<h2 id="non-superato">{ic("attenzione")}Se non superi una parte</h2>
<p>{con_mail(escape(voci["non_superato"]["testo"]))}</p>
{fonte_risultati(s, "non_superato")}
<p><a href="../../risultati/{SLUG_RISULTATI[s]}/">Risultati {escape(s)}: dove vederli e quando escono</a></p>
</section>
<section>
<h2 id="come-usare">{ic("matita")}Come usare questo esempio</h2>
<ol class="passi">{passi}</ol>
</section>
<div class="due">
<section>
<h2 id="date">{ic("cal")}Prossime date {escape(s)} (livello B1)</h2>
{date_ente_html(prossime, s, "../../")}
</section>
<aside>{modulo()}</aside>
</div>
{riquadro_preparati("../../", gratis="#file")}
<section>
<h2 id="domande">{ic("info")}Domande frequenti sull'esempio {escape(s)}</h2>
{faq_html}
</section>
<section>
<h2>{ic("libro")}Esempi degli altri enti</h2>
<div class="altre"><a href="../">Tutti gli esempi</a>{altri}<a href="../confronto/">I 4 esami a confronto</a><a href="../../esonero-test-italiano/">Chi è esonerato</a></div>
<h2>{ic("info")}Altre domande</h2>
{link_guide("../../", salta="esempi/", dopo_b1=False)}
</section>"""
    n = len(e["file"])
    sup = t["superare"]
    descr = descrizione_pagina(
        f"{e['esame']}: esempio d'esame ufficiale gratis ({n} file: {', '.join(formati)}), com'è fatta ogni prova, durata e punteggio per superare: {sup}.",
        f"{e['esame']}: esempio d'esame ufficiale gratis ({', '.join(formati)}), com'è fatta ogni prova e punteggio per superare: {sup}.",
        f"{e['esame']}: esempio d'esame ufficiale gratis, com'è fatta ogni prova, quanto dura e punteggio per superare: {sup}.",
        f"{e['esame']}: esempio d'esame ufficiale gratis ({', '.join(formati)}), prove, durata, punteggio per superare e cosa fare se non superi.")
    pagina(f"esempi/{sl}/index.html", titolo_pagina(TITOLI_ESEMPI[s][0]), descr, corpo, jsonld)


def pagina_confronto(prossime):
    """/esempi/confronto/: i 4 esami B1 a confronto (durata, prove, scrittura, orale, punteggio, recupero, costo, sedi)."""
    v = data_breve(esempi["verificato_il"])
    vr = data_breve(RISULTATI["verificato_il"])
    righe_breve = []
    for s in ENTE:
        en = ENTE[s]
        orale = next(p for p in ES[s]["prove"] if p["nome"] in ("Orale", "Parlare"))
        p = prossima_di(prossime, [s])
        prossimo = f'{data_breve(p["data"])}' if p else "nessuna data nuova pubblicata"
        righe_breve.append(
            f'<tr><td>{eb(s)}<strong>{escape(ES[s]["esame"])}</strong><br><a class="ris-guida" href="../{SLUG_ENTE[s]}/">Esempio {escape(s)} {ic("freccia")}</a></td>'
            f'<td data-l="Quanto dura">{escape(en["fatti"]["durata"]["prove"]["totale"])}</td>'
            f'<td data-l="Orale">{escape(orale["tempo"])}</td>'
            f'<td data-l="Per superare">{escape(RISULTATI["enti"][s]["tabella"]["superare"])}</td>'
            f'<td data-l="Se non superi una parte">{escape(RISULTATI["enti"][s]["tabella"]["ripeti"])}</td>'
            f'<td data-l="Costo">{escape(en["fatti"]["costo"]["breve"])}</td>'
            f'<td data-l="Prossima data B1">{escape(prossimo)}<br><span class="small">{sum(1 for x in sedi if x["ente"] == s)} sedi in Italia</span></td></tr>')
    tab_breve = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Esame</th><th scope="col">Quanto dura</th><th scope="col">Orale</th>'
                 '<th scope="col">Per superare</th><th scope="col">Se non superi una parte</th><th scope="col">Costo</th><th scope="col">Prossima data B1</th></tr></thead>'
                 f'<tbody>{"".join(righe_breve)}</tbody></table></div>')

    def prova_di(s, *nomi):
        p = next(x for x in ES[s]["prove"] if x["nome"].split(" (")[0] in nomi)
        return f'{escape(p["cosa"])} <span class="small">({escape(p["tempo"])})</span>'
    colonne = [("Ascolto", ("Ascolto", "Ascoltare")), ("Lettura", ("Lettura", "Lettura e grammatica", "Leggere")),
               ("Scrittura", ("Scrittura", "Scrivere")), ("Orale", ("Orale", "Parlare"))]
    righe_prove = "".join(
        f'<tr><td>{eb(s)}<strong>{escape(ES[s]["esame"])}</strong></td>'
        + "".join(f'<td data-l="{c}">{prova_di(s, *nomi)}</td>' for c, nomi in colonne) + "</tr>" for s in ENTE)
    tab_prove = ('<div class="tab-wrap ris-tab cf-tab"><table class="conf"><thead><tr><th scope="col">Esame</th>'
                 + "".join(f'<th scope="col">{c}</th>' for c, _ in colonne) + f'</tr></thead><tbody>{righe_prove}</tbody></table></div>')
    fonti_tutte = " · ".join(f'{escape(s)}: {link_fonti(ES[s]["fonti_struttura"][:1])}' for s in ENTE)
    citt = "".join(f'<li><span>{eb(s)} {escape(ENTE[s]["cittadinanza"])}</span></li>' for s in ENTE)
    vade = esoneri["fonti"]["vademecum"]
    faq = [
        ("Qual è l'esame B1 più facile per la cittadinanza?",
         "Nessun ente dice che il suo esame è più facile, e non lo diciamo noi. Gli esami sono diversi: CILS B1 Cittadinanza ha una sola email da scrivere ma non permette di rifare solo una parte; "
         "PLIDA chiede 18 punti su 30 in ogni abilità e permette di recuperare le abilità non superate per 18 mesi; CELI 2 i ha un orale con domande di educazione civica; "
         "CERT.IT a Roma Tre si fa al computer. Il modo migliore per scegliere è fare due prove d'esempio ufficiali e vedere dove vai meglio."),
        ("Che differenza c'è tra CILS, CELI e PLIDA?",
         "Tutti e tre hanno ascolto, lettura, scrittura e orale. Cambiano i tempi (CILS circa 2 ore, CELI 2 i 2 ore e 30 minuti, PLIDA circa 2 ore e 35 minuti), le prove di scrittura "
         "(CILS un'email di 80-120 parole; CELI risposte brevi, un'email di 40-50 e un messaggio di 80-90; PLIDA due testi di 110-150 e 70-100), l'orale e le regole se non superi una parte."),
        ("Quanto dura l'esame B1 per la cittadinanza?",
         "Sommando i tempi delle prove scritti dagli enti: CERT.IT 1 ora e 40 minuti, CILS B1 Cittadinanza circa 2 ore, CELI 2 i 2 ore e 30 minuti (dato dell'ente), PLIDA B1 circa 2 ore e 35 minuti. "
         "L'orale dura da 10 a 15 minuti e di solito si fa dopo lo scritto."),
        ("Posso rifare solo la parte che non ho superato?",
         "Dipende dall'ente. CILS B1 Cittadinanza: no, si rifà tutto l'esame. CELI: entro un anno rifai solo lo scritto o solo l'orale, pagando il 70% della tassa. "
         "PLIDA: entro 18 mesi recuperi da 1 a 3 abilità, anche in un altro centro. CERT.IT: il sito non lo dice per il B1, chiedi alla sede."),
        ("Per la cittadinanza vale qualunque dei 4 esami?",
         "Il Vademecum del Ministero dell'Interno (aprile 2025) elenca come enti certificatori riconosciuti l'Università per Stranieri di Siena (CILS), l'Università per Stranieri di Perugia (CELI), "
         "l'Università Roma Tre (CERT.IT), la Società Dante Alighieri (PLIDA) e l'Università per Stranieri «Dante Alighieri» di Reggio Calabria (che questo sito non tratta). Il certificato deve essere almeno di livello B1. Per il tuo caso chiedi alla Prefettura."),
    ]
    jsonld, faq_html = faq_html_e_jsonld(faq)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), ("Prove d'esempio", "../"), ("Confronto", None))}
<span class="occhiello">{ic("lista")}Fonti ufficiali · controllato il {v}</span>
<h1>CILS, CELI, PLIDA o CERT.IT: l'esame B1 per la cittadinanza a confronto</h1>
<p class="lead">Secondo i documenti ufficiali dei 4 enti (sillabi, descrizioni dell'esame e pagine del livello B1, controllati il {v}), tutti e quattro gli esami hanno ascolto, lettura, scrittura e orale.
Cambiano la durata, il tipo di domande, il punteggio per superare e cosa succede se non superi una parte.</p>
</section>
<section>
<h2 id="in-breve">{ic("orologio")}In breve: durata, punteggio, recupero, costo</h2>
{tab_breve}
<div class="fonte">{ic("doc")}<span>Fonti: durata da sillabi e descrizioni ufficiali (somma dei tempi delle prove, se l'ente non dà il totale); punteggi e recupero dalle pagine e dai regolamenti degli enti, letti il {vr}; costo dalle pagine ufficiali (<a href="../../costo/">tutti i costi</a>); date e sedi dal nostro <a href="../../#date">calendario</a>.</span></div>
</section>
<section>
<h2 id="prove">{ic("lista")}Prova per prova: cosa devi fare</h2>
<p>Le stesse quattro abilità, ma domande diverse. Nel CELI 2 i lettura e scrittura si fanno insieme in 2 ore; nel CERT.IT ascolto, lettura e scrittura in 90 minuti in tutto.</p>
{tab_prove}
<div class="fonte">{ic("doc")}<span>Fonti: {fonti_tutte} · controllato il {v}</span></div>
</section>
<section>
<h2 id="differenze">{ic("info")}Le differenze che contano</h2>
<ul class="cifre" style="flex-direction:column;align-items:flex-start;gap:10px">
<li>{ic("attenzione")}<span><strong>Se non superi una parte.</strong> CILS B1 Cittadinanza: rifai tutto. CELI: rifai solo lo scritto o solo l'orale entro un anno (70% della tassa). PLIDA: recuperi fino a 3 abilità entro 18 mesi, anche in un altro centro. CERT.IT: il sito non lo dice per il B1.</span></li>
<li>{ic("matita")}<span><strong>Scrittura.</strong> CILS: un'email di 80-120 parole. CELI 2 i: 4 risposte brevi, un'email di 40-50 parole, un messaggio di 80-90. PLIDA: due testi di 110-150 e 70-100 parole. CERT.IT: due testi di 50-80 parole.</span></li>
<li>{ic("voce")}<span><strong>Orale.</strong> CILS: presentazione e dialogo, circa 10 minuti. CELI 2 i: 5 compiti in 10-12 minuti, con domande di educazione civica. PLIDA: interazione (anche con un altro candidato) e monologo, circa 15 minuti. CERT.IT: intervista, simulazione di ruolo e monologo in 10 minuti.</span></li>
<li>{ic("web")}<span><strong>Su carta o al computer.</strong> A Roma Tre lo scritto del CERT.IT B1 si fa al computer; negli esempi degli altri enti le risposte si scrivono sul foglio delle risposte.</span></li>
</ul>
<h3>Esame «cittadinanza» o B1 normale?</h3>
<ul class="cifre" style="flex-direction:column;align-items:flex-start;gap:8px">{citt}</ul>
</section>
<section>
<h2 id="scegliere">{ic("ok")}Come scegliere</h2>
<p>Nessun ente scrive che il suo esame è più facile, e non lo diciamo noi. Per decidere guarda tre cose: <strong>la data</strong> (quale sessione arriva prima, con l'iscrizione ancora aperta),
<strong>la sede</strong> (quale ente ha una sede vicino a te) e <strong>il tipo di prove</strong>: fai la prova d'esempio di due enti con i tempi veri e scegli quella in cui vai meglio.
Il <a href="{escape(vade["url"])}" rel="noopener">Vademecum del Ministero dell'Interno</a> elenca gli enti certificatori riconosciuti: ci sono tutti e quattro, più l'Università per Stranieri «Dante Alighieri» di Reggio Calabria.</p>
<div class="altre">{"".join(f'<a href="../{SLUG_ENTE[s]}/">Esempio {escape(s)}</a>' for s in ENTE)}<a href="../../#date">Tutte le date</a><a href="../../#citta">Sedi per città</a></div>
</section>
<div class="due">
<section>
<h2 id="domande">{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<aside>{modulo()}</aside>
</div>
{riquadro_preparati("../../", gratis="../")}
<section>
<h2>{ic("info")}Altre domande</h2>
{link_guide("../../", salta="esempi/confronto/", dopo_b1=False)}
</section>"""
    pagina("esempi/confronto/index.html",
           titolo_pagina("CILS, CELI, PLIDA o CERT.IT? Differenze dell'esame B1"),
           descrizione_pagina("CILS, CELI, PLIDA e CERT.IT a confronto: durata dell'esame B1 per la cittadinanza, prove, orale, punteggio per superare, "
                              "recupero e costo, con le fonti."), corpo, jsonld)


def pagina_esonero():
    """/esonero-test-italiano/: chi è esonerato dal certificato B1 per la cittadinanza e dal test A2 per il permesso UE di lungo periodo.
    Solo regole lette nelle fonti ufficiali di dati/esoneri.json (frasi controllate da raccolta/esempi.py). Decide la Prefettura/Questura."""
    F = esoneri["fonti"]
    v = data_breve(esoneri["verificato_il"])

    def a(chiave, testo=None):
        return f'<a href="{escape(F[chiave]["url"])}" rel="noopener">{escape(testo or F[chiave]["nome"])}</a>'

    def fonte(*chiavi):
        return f'<div class="fonte">{ic("doc")}<span>{"Fonte" if len(chiavi) == 1 else "Fonti"}: {" · ".join(a(k) for k in chiavi)} · {"letta" if len(chiavi) == 1 else "lette"} il {v}</span></div>'

    def scheda(icona, titolo, testo, *chiavi):
        return (f'<div class="fatto"><div class="f-et">{ic(icona)}<span>{titolo}</span></div><p>{testo}</p>{fonte(*chiavi)}</div>')

    citt = '<div class="fatti">' + scheda(
        "ok", "Chi ha firmato l'accordo di integrazione",
        "È escluso dall'obbligo chi ha sottoscritto l'accordo di integrazione (art. 4-bis del Testo unico sull'immigrazione). Il Vademecum del Ministero precisa: "
        "sono le persone entrate in Italia con il ricongiungimento o la coesione familiare, che lo dimostrano con l'attestazione della Prefettura (Sportello unico) "
        "e scrivono nella domanda gli estremi dell'accordo.", "legge91", "vademecum") + scheda(
        "ok", "Chi ha il permesso UE per soggiornanti di lungo periodo",
        "È escluso chi ha il permesso di soggiorno UE per soggiornanti di lungo periodo (la «carta di soggiorno»). Secondo il Vademecum vale anche il vecchio permesso «CE» "
        "per soggiornanti di lungo periodo, se rilasciato dal 9 dicembre 2010, quando è entrato in vigore il test di italiano.", "legge91", "vademecum") + scheda(
        "info", "Chi ha gravi limitazioni nell'imparare la lingua",
        "Con la sentenza n. 25 del 2025 la Corte costituzionale ha esonerato chi ha gravi limitazioni alla capacità di imparare la lingua per l'età, per malattie o per disabilità. "
        "Serve un certificato di una <strong>struttura sanitaria pubblica</strong>: secondo il Ministero non basta il certificato del medico di base. "
        "Chi vive in Italia e ha un certificato medico straniero deve aggiungere quello di una struttura sanitaria pubblica italiana; chi vive all'estero presenta il certificato "
        "straniero tradotto e legalizzato.", "corte25", "circ14605", "vademecum") + scheda(
        "doc", "Al posto del certificato: un titolo di studio in italiano",
        "Chi non è esonerato può presentare, al posto del certificato B1, un titolo di studio di un istituto pubblico o paritario riconosciuto, dalla scuola secondaria di primo grado "
        "(la scuola media) in su, preso <strong>in lingua italiana</strong>. Se il titolo viene da un ente pubblico basta l'autocertificazione con gli estremi; se viene da un istituto "
        "paritario o privato serve una copia autenticata.", "legge91", "vademecum") + "</div>"

    devono = f"""<ul class="cifre" style="flex-direction:column;align-items:flex-start;gap:8px">
<li>{ic("attenzione")}<span>i <strong>cittadini dell'Unione europea</strong>;</span></li>
<li>{ic("attenzione")}<span>chi ha la <strong>carta di soggiorno per familiare</strong> o coniuge di cittadino italiano o dell'Unione: non è il permesso UE per soggiornanti di lungo periodo;</span></li>
<li>{ic("attenzione")}<span>i cittadini britannici e i loro familiari con la carta di soggiorno dell'Accordo di recesso («Brexit»).</span></li>
</ul>"""

    a2_non = '<div class="fatti">' + scheda(
        "ok", "Figli sotto i 14 anni",
        "Il decreto non si applica ai figli minori di 14 anni, anche nati fuori dal matrimonio, del richiedente e del coniuge.", "dm2021") + scheda(
        "info", "Gravi limitazioni certificate",
        "Non fa il test chi ha gravi limitazioni nell'imparare la lingua per età, malattie o handicap, con certificato di una struttura sanitaria pubblica, "
        "da allegare alla domanda di permesso.", "dm2021") + scheda(
        "doc", "Chi ha già un certificato almeno A2",
        "Un certificato di livello A2 o superiore di un ente riconosciuto: l'allegato A del decreto elenca Università Roma Tre (CERT.IT), Università per Stranieri di Perugia (CELI), "
        "Università per Stranieri di Siena (CILS), Società Dante Alighieri (PLIDA) e Università per Stranieri «Dante Alighieri» di Reggio Calabria. "
        "Quindi anche il certificato B1 fatto per la cittadinanza.", "dm2021") + scheda(
        "doc", "Corso al CPIA o accordo di integrazione con livello A2",
        "Chi ha fatto un corso di italiano in un CPIA (Centro provinciale per l'istruzione degli adulti) e ha un titolo finale almeno A2; "
        "chi ha avuto riconosciuto il livello A2 nei crediti dell'accordo di integrazione.", "dm2021") + scheda(
        "doc", "Diploma o università in Italia",
        "Chi ha il diploma di scuola secondaria di primo o secondo grado (scuola media o superiore) di una scuola italiana o di un CPIA, "
        "chi è iscritto a un'università italiana, o fa in Italia un dottorato o un master universitario.", "dm2021") + scheda(
        "doc", "Alcuni lavoratori",
        "Chi è entrato in Italia ed è dirigente o lavoratore altamente qualificato, professore universitario o ricercatore, traduttore o interprete, "
        "giornalista accreditato (art. 27, comma 1, lettere a, c, d e q del Testo unico).", "dm2021", "minint_test") + scheda(
        "scudo", "Protezione internazionale e ricerca",
        "Secondo l'art. 9 del Testo unico il test non si applica a chi ha la protezione internazionale e non è richiesto per il permesso rilasciato per attività di ricerca "
        "presso università ed enti vigilati dal Ministero dell'Università.", "tu9") + "</div>"

    righe = [
        ("Accordo di integrazione firmato", "Esonerato", "Fa il test, salvo livello A2 riconosciuto nei crediti dell'accordo"),
        ("Permesso UE per soggiornanti di lungo periodo", "Esonerato", "Non serve: è il permesso che già hai"),
        ("Gravi limitazioni certificate da una struttura sanitaria pubblica", "Esonerato", "Esonerato"),
        ("Certificato di italiano A2 di un ente riconosciuto", "Non basta: serve almeno B1", "Non fa il test"),
        ("Certificato B1 di un ente riconosciuto", "Vale", "Non fa il test"),
        ("Diploma di scuola media o superiore italiana", "Vale al posto del certificato (titolo in italiano)", "Non fa il test"),
        ("Figlio sotto i 14 anni", "Non trattato nelle fonti lette", "Non fa il test"),
        ("Cittadino dell'Unione europea o familiare con carta di soggiorno per familiare", "Deve avere il B1", "Non trattato nelle fonti lette"),
    ]
    tab = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Il tuo caso</th><th scope="col">Cittadinanza (certificato B1)</th>'
           '<th scope="col">Carta di soggiorno (test A2)</th></tr></thead><tbody>'
           + "".join(f'<tr><td><strong>{escape(c)}</strong></td><td data-l="Cittadinanza (B1)">{escape(b1)}</td><td data-l="Carta di soggiorno (A2)">{escape(a2)}</td></tr>'
                     for c, b1, a2 in righe) + "</tbody></table></div>")

    faq = [
        ("Chi è esonerato dall'esame B1 per la cittadinanza?",
         "Secondo l'art. 9.1 della legge 91/1992 e il Vademecum del Ministero dell'Interno: chi ha firmato l'accordo di integrazione, chi ha il permesso di soggiorno UE per soggiornanti "
         "di lungo periodo (anche il vecchio permesso CE rilasciato dal 9 dicembre 2010) e, dal 2025, chi ha gravi limitazioni nell'imparare la lingua certificate da una struttura sanitaria pubblica. "
         "Al posto del certificato vale un titolo di studio in italiano di una scuola pubblica o paritaria, dalla scuola media in su. Decide la Prefettura."),
        ("Ho la carta di soggiorno: devo fare l'esame B1 per la cittadinanza?",
         "Se la tua carta è il permesso di soggiorno UE per soggiornanti di lungo periodo, la legge ti esclude dall'obbligo del certificato. Non vale per la carta di soggiorno per familiare "
         "di cittadino italiano o dell'Unione: in quel caso il Ministero chiede il B1."),
        ("Con un certificato medico posso non fare l'esame B1?",
         "Sì, se il certificato è di una struttura sanitaria pubblica e attesta gravi limitazioni nell'imparare la lingua per età, malattie o disabilità (sentenza n. 25/2025 della Corte costituzionale). "
         "Il Ministero dell'Interno (circolare n. 14605 del 13 marzo 2025) scrive che non basta il certificato del medico di base."),
        ("Ho un diploma italiano: devo fare l'esame B1?",
         "No, se è un titolo di una scuola pubblica o paritaria, dalla scuola media in su, preso in lingua italiana: vale al posto del certificato. Per un titolo di un ente pubblico basta "
         "l'autocertificazione; per un istituto paritario o privato serve la copia autenticata."),
        ("Chi non deve fare il test di italiano A2 per la carta di soggiorno?",
         "Secondo il decreto del Ministro dell'Interno del 7 dicembre 2021: i figli sotto i 14 anni, chi ha gravi limitazioni certificate da una struttura sanitaria pubblica, chi ha un certificato "
         "almeno A2 di un ente riconosciuto, chi ha un titolo A2 di un corso al CPIA o il livello A2 nei crediti dell'accordo di integrazione, chi ha un diploma di scuola media o superiore italiana "
         "o studia in un'università italiana, e alcuni lavoratori entrati con l'art. 27 del Testo unico. Il Testo unico esclude anche chi ha la protezione internazionale."),
        ("Il certificato B1 vale anche per la carta di soggiorno?",
         "Sì: il decreto del 7 dicembre 2021 esonera dal test chi ha un certificato di livello almeno A2 di uno degli enti dell'allegato A (Roma Tre, Stranieri di Perugia, Stranieri di Siena, "
         "Società Dante Alighieri, Stranieri «Dante Alighieri» di Reggio Calabria). Il certificato si allega in copia autentica."),
        ("Se non supero il test A2, quando posso rifarlo?",
         "Il Ministero dell'Interno scrive che puoi chiedere di ripetere il test con la stessa procedura online, ma solo dopo 90 giorni dalla data dell'esame precedente."),
    ]
    jsonld, faq_html = faq_html_e_jsonld(faq)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Chi è esonerato", None))}
<span class="occhiello">{ic("scudo")}Legge, decreti e Ministero · letti il {v}</span>
<h1>Chi è esonerato dal test di italiano: cittadinanza (B1) e carta di soggiorno (A2)</h1>
<p class="lead">Secondo l'art. 9.1 della legge 91/1992 (testo in vigore letto su Normattiva il {v}) e il Vademecum del Ministero dell'Interno (circolare n. 20475 del 23 aprile 2025),
per la cittadinanza non deve presentare il certificato B1 chi ha firmato l'accordo di integrazione, chi ha il permesso UE per soggiornanti di lungo periodo e chi ha gravi limitazioni certificate
da una struttura sanitaria pubblica. Per la carta di soggiorno il test A2 della Prefettura non serve, per esempio, a chi ha già un certificato almeno A2 o un diploma italiano (decreto del Ministro dell'Interno 7 dicembre 2021).</p>
<nav class="es-vai" aria-label="Vai alla sezione"><a href="#cittadinanza"><span class="ri"><strong>Cittadinanza</strong>{ic("giu")}</span><span>Esame B1</span><small>chi è esonerato, titolo di studio</small></a>
<a href="#carta-di-soggiorno"><span class="ri"><strong>Carta di soggiorno</strong>{ic("giu")}</span><span>Test A2 della Prefettura</span><small>chi non lo fa, come funziona</small></a></nav>
</section>
{avviso("Questa pagina riassume le regole scritte nelle fonti ufficiali, ma <strong>decide sempre l'ufficio</strong>: la Prefettura per la cittadinanza, la Questura per il permesso UE di lungo periodo. Questo sito non dà consulenza: per il tuo caso chiedi a loro o a un patronato.")}
<section>
<h2 id="riepilogo">{ic("lista")}Riepilogo: il tuo caso</h2>
{tab}
<div class="fonte">{ic("doc")}<span>Fonti: {a("legge91")} · {a("vademecum")} · {a("dm2021")} · lette il {v}. Le righe sono spiegate più sotto, con le fonti di ogni regola.</span></div>
</section>
<div class="due">
<section>
<h2 id="cittadinanza">{ic("scudo")}Cittadinanza: chi non deve presentare il certificato B1</h2>
<p>Dal 4 dicembre 2018 chi chiede la cittadinanza per matrimonio o per residenza (articoli 5 e 9 della legge 91/1992) deve avere una conoscenza dell'italiano almeno di livello B1.
La legge e il Ministero dell'Interno escludono questi casi:</p>
{citt}
<h3>Chi deve avere comunque il B1</h3>
<p>Secondo il Vademecum del Ministero restano obbligati:</p>
{devono}
<h3>Quali certificati valgono</h3>
<p>Un certificato almeno B1 di un ente certificatore riconosciuto. Il Vademecum elenca: Università per Stranieri di Siena (CILS), Università per Stranieri di Perugia (CELI),
Università Roma Tre (CERT.IT), Società Dante Alighieri (PLIDA) e Università per Stranieri «Dante Alighieri» di Reggio Calabria. Il certificato si può prendere anche nei CPIA.
<strong>Non valgono</strong> i certificati dei corsi di qualificazione professionale regionali.</p>
{fonte("vademecum", "domanda")}
<p><a href="../#date">Date dell'esame B1</a> · <a href="../esempi/">Prove d'esempio ufficiali</a> · <a href="../esempi/confronto/">I 4 esami a confronto</a></p>
</section>
<aside>{modulo()}</aside>
</div>
<section>
<h2 id="carta-di-soggiorno">{ic("doc")}Carta di soggiorno: il test di italiano A2</h2>
<p>Per avere il permesso di soggiorno UE per soggiornanti di lungo periodo (la «carta di soggiorno») bisogna superare un test di conoscenza dell'italiano (art. 9, comma 2-bis, del Testo unico).
Il livello richiesto è l'<strong>A2</strong>: capire frasi ed espressioni di uso frequente. Le regole sono nel decreto del Ministro dell'Interno del 7 dicembre 2021, che ha sostituito
il decreto del 4 giugno 2010 (alcune pagine di Prefetture e del Ministero citano ancora quello del 2010: i casi di esonero sono scritti allo stesso modo).</p>
{fonte("tu9", "dm2021")}
<h3>Come funziona il test</h3>
<ol class="passi">
<li><span>Fai la domanda online alla Prefettura della provincia dove abiti, sul {a("portale", "Portale Servizi del Ministero dell'Interno")}.</span></li>
<li><span>La Prefettura ti convoca entro 60 giorni, con giorno, ora e luogo.</span></li>
<li><span>Il test si fa al computer; se lo chiedi, su carta. Controlla che tu capisca brevi testi e sappia interagire. Per esempio la Prefettura di Lecco descrive tre prove: comprensione orale (25 minuti), comprensione scritta (25 minuti) e interazione scritta (10 minuti).</span></li>
<li><span>Per superarlo serve almeno l'<strong>80%</strong> del punteggio. Il risultato va alla Questura, che rilascia il permesso se ci sono gli altri requisiti.</span></li>
<li><span>Se non lo superi puoi rifarlo con una nuova domanda: secondo il Ministero solo dopo 90 giorni dall'esame precedente.</span></li>
</ol>
{fonte("dm2021", "minint_test", "lecco")}
<h3 id="a2-esonero">Chi non fa il test A2</h3>
{a2_non}
<p class="ris-nota">Con il certificato, il titolo del CPIA o il diploma alleghi alla domanda di permesso una copia autentica; per l'accordo di integrazione o il lavoro dell'art. 27 basta una dichiarazione.
Dal 2025 il Ministero dell'Università tiene un elenco degli enti certificatori: i cinque enti del decreto sono inseriti per un anno, poi controllati ({a("mur959", "decreto n. 959 del 14 novembre 2025")}).</p>
</section>
<section>
<h2 id="due-usi">{ic("ok")}Un certificato, due usi</h2>
<p>Chi ha il permesso UE per soggiornanti di lungo periodo è esonerato dal B1 per la cittadinanza. E chi ha già un certificato B1 di un ente riconosciuto non deve fare il test A2 per la carta di soggiorno:
il decreto chiede un certificato «non inferiore» all'A2.</p>
{fonte("legge91", "dm2021")}
</section>
<section>
<h2 id="domande">{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<h2>{ic("info")}Altre domande</h2>
{link_guide("../", salta="esonero-test-italiano/", dopo_b1=False)}
</section>"""
    pagina("esonero-test-italiano/index.html",
           titolo_pagina("Esonero test di italiano: cittadinanza B1 e carta di soggiorno"),
           descrizione_pagina("Chi non deve fare l'esame B1 per la cittadinanza o il test A2 per la carta di soggiorno: accordo di integrazione, permesso UE, "
                              "certificato medico, diploma."), corpo, jsonld)


# ---------------------------------------------------------------- reddito per il ricongiungimento familiare (dal 30/10/2026)
def euro(x):
    """Decimal → «10.651,68 €» (due decimali, punto per le migliaia, virgola per i decimali)."""
    s = f"{x.quantize(Decimal('0.01')):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def tabella_ricongiungimento():
    """Righe della tabella: (familiari, reddito annuo, al mese su 12, al mese su 13). Regola dell'art. 29 c. 3 lett. b) del Testo unico:
    assegno sociale annuo + metà dell'assegno sociale per ogni familiare. Importi esatti al centesimo (l'assegno annuo è pari)."""
    a = RICONG["assegno_sociale"]
    annuo = Decimal(a["annuo"])
    righe = []
    for n in RICONG["familiari"]:
        tot = annuo + annuo / 2 * n
        righe.append((n, tot, tot / 12, tot / 13))
    return righe


def controlli_ricongiungimento():
    """Controlli dei dati del ricongiungimento: fonte e data, annuo = mensile × mensilità, numeri della tabella. Avviso dal nuovo anno."""
    a, r = RICONG["assegno_sociale"], RICONG["regola"]
    errori = []
    for voce in (a, r, RICONG["sportello"]):
        if not voce.get("url") or not voce.get("verificato_il"):
            errori.append(f"ricongiungimento.json: voce senza url o verificato_il: {voce.get('fonte') or voce.get('norma') or voce.get('nome')}")
    if Decimal(a["mensile"]) * a["mensilita"] != Decimal(a["annuo"]):
        errori.append(f"ricongiungimento.json: {a['mensile']} × {a['mensilita']} non fa {a['annuo']}")
    if a["anno"] != RICONG["anno"]:
        errori.append("ricongiungimento.json: anno dell'assegno sociale diverso da «anno»")
    righe = tabella_ricongiungimento()
    if [n for n, *_ in righe] != list(range(1, len(righe) + 1)) or any(righe[i][1] >= righe[i + 1][1] for i in range(len(righe) - 1)):
        errori.append("ricongiungimento.json: tabella dei familiari non in ordine")
    if righe[0][1] != Decimal(a["annuo"]) * Decimal("1.5"):
        errori.append("ricongiungimento: riga di 1 familiare diversa da 1,5 volte l'assegno sociale")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))
    if OGGI.year > RICONG["anno"]:
        print(f"AVVISO: dati/ricongiungimento.json usa l'assegno sociale {RICONG['anno']}: aggiornarlo con la circolare INPS del {OGGI.year} "
              "(vedi NOTE.md, «Reddito per il ricongiungimento»).", file=sys.stderr)


def pagina_ricongiungimento():
    """Reddito minimo per il ricongiungimento familiare (art. 29 c. 3 lett. b del Testo unico immigrazione) con l'assegno sociale INPS dell'anno.
    Nessun riquadro «Preparati alla prova orale»: la pagina non riguarda l'esame. Nessun consiglio sul caso personale."""
    a, r, sp = RICONG["assegno_sociale"], RICONG["regola"], RICONG["sportello"]
    anno = RICONG["anno"]
    mens, annuo = Decimal(a["mensile"]), Decimal(a["annuo"])
    meta = annuo / 2
    doppio = annuo * 2
    righe = tabella_ricongiungimento()
    uno = righe[0]
    tre = next(x for x in righe if x[0] == 3)
    quattro = next(x for x in righe if x[0] == 4)
    verifica = f"controllato il {data_breve(a['verificato_il'])}"
    data_v = data_breve(a["verificato_il"])
    fonte_inps = f'<a href="{escape(a["url"])}" rel="noopener">INPS, circolare n. 153 del 19 dicembre 2025</a>'
    fonte_tab = f'<a href="{escape(a["url_allegato"])}" rel="noopener">allegato n. 2, tabella A (PDF)</a>'
    fonte_legge = f'<a href="{escape(r["url"])}" rel="noopener">art. 29 del Testo unico immigrazione (d.lgs. 286/1998) su Normattiva</a>'
    fonte_sui = f'<a href="{escape(sp["url"])}" rel="noopener">{escape(sp["nome"])}</a>'

    def chi(n):
        return {1: "per esempio moglie, marito o 1 figlio", 2: "per esempio moglie e 1 figlio, o 2 figli",
                3: "per esempio moglie e 2 figli", 4: "per esempio moglie e 3 figli", 5: "per esempio moglie e 4 figli"}.get(n, "")

    righe_html = "".join(
        f'<tr><td><strong>{n} {"familiare" if n == 1 else "familiari"}</strong><br><span class="small">{chi(n)}</span></td>'
        f'<td data-l="Persone in famiglia, con te">{n + 1} persone</td><td data-l="All\'anno"><strong>{euro(tot)}</strong></td>'
        f'<td data-l="Al mese, su 12 mesi">{euro(m12)}</td><td data-l="Al mese, su 13 mensilità">{euro(m13)}</td></tr>'
        for n, tot, m12, m13 in righe)
    righe_html += (f'<tr><td><strong>2 o più figli sotto i 14 anni</strong><br><span class="small">regola speciale della legge, vedi sotto</span></td>'
                   f'<td class="rc-vuota">–</td><td data-l="All\'anno"><strong>{euro(doppio)}</strong></td>'
                   f'<td data-l="Al mese, su 12 mesi">{euro(doppio / 12)}</td><td data-l="Al mese, su 13 mensilità">{euro(doppio / 13)}</td></tr>')
    tabella = (f'<div class="tab-wrap rc-tab"><table class="conf"><caption class="small">Reddito minimo {anno} per il ricongiungimento familiare, '
               f'con l\'assegno sociale {anno} di {euro(annuo)} l\'anno</caption>'
               '<thead><tr><th scope="col">Familiari da far venire</th><th scope="col">Persone in famiglia, con te</th><th scope="col">Reddito minimo all\'anno</th>'
               '<th scope="col">Al mese, su 12 mesi</th><th scope="col">Al mese, su 13 mensilità</th></tr></thead>'
               f'<tbody>{righe_html}</tbody></table></div>'
               f'<div class="fonte">{ic("doc")}<span>Fonti: assegno sociale {anno}: {fonte_inps}, {fonte_tab} · regola: {fonte_legge} · {verifica}</span></div>')

    risposta_breve = (f"Nel {anno} per il ricongiungimento familiare serve un reddito di almeno {euro(uno[1])} l'anno con 1 familiare, "
                      f"più {euro(meta)} per ogni familiare in più. È l'assegno sociale {anno} ({euro(annuo)} l'anno, circolare INPS n. 153 del 19/12/2025) "
                      f"aumentato della metà per ogni familiare, come dice l'art. 29 del Testo unico immigrazione. Dati controllati il {data_v}.")

    faq = [
        (f"Quanto reddito serve per il ricongiungimento familiare nel {anno}?",
         f"Serve un reddito annuo di almeno {euro(uno[1])} per 1 familiare, {euro(righe[1][1])} per 2, {euro(tre[1])} per 3, {euro(quattro[1])} per 4 "
         f"e {euro(righe[4][1])} per 5. Il calcolo è l'assegno sociale {anno} ({euro(annuo)} l'anno, fonte INPS) più la metà ({euro(meta)}) "
         "per ogni familiare da far venire (art. 29 del Testo unico immigrazione)."),
        ("Qual è il reddito minimo per il ricongiungimento della moglie (o del marito) o di 1 figlio?",
         f"Per 1 familiare servono almeno {euro(uno[1])} l'anno, cioè circa {euro(uno[2])} al mese su 12 mesi. "
         f"Per la moglie e 1 figlio (2 familiari) servono {euro(righe[1][1])} l'anno."),
        (f"Quanto reddito serve per il ricongiungimento familiare per 4 persone nel {anno}?",
         f"Dipende da come conti. Se 4 persone sono tutta la famiglia, tu compreso (per esempio tu, moglie e 2 figli), i familiari da far venire sono 3: "
         f"servono {euro(tre[1])} l'anno. Se i familiari da far venire sono 4, servono {euro(quattro[1])} l'anno."),
        ("Qual è la tabella del reddito per il ricongiungimento familiare?",
         f"1 familiare {euro(uno[1])}; 2 familiari {euro(righe[1][1])}; 3 familiari {euro(tre[1])}; 4 familiari {euro(quattro[1])}; "
         f"5 familiari {euro(righe[4][1])}; 2 o più figli sotto i 14 anni: almeno {euro(doppio)}, il doppio dell'assegno sociale. Importi annui {anno}."),
        ("Il reddito di mia moglie o di altri familiari conta?",
         "Sì, se vivono già con te in Italia: la legge dice che si tiene conto anche del reddito annuo complessivo dei familiari conviventi. "
         "Il reddito deve venire da fonti lecite. Quali documenti presentare te lo dice lo Sportello unico per l'immigrazione."),
        ("Dove si fa la domanda di ricongiungimento familiare?",
         "Allo Sportello unico per l'immigrazione della Prefettura della provincia dove vivi, online, sul Portale Servizi del Ministero dell'Interno "
         "(accesso con SPID o CIE). Per legge il nulla osta va rilasciato entro 150 giorni dalla richiesta."),
        (f"L'importo cambia nel {anno + 1}?",
         f"Sì: l'assegno sociale cambia ogni anno dal 1° gennaio e l'INPS pubblica il nuovo importo in una circolare (quello del {anno} è uscito il 19 dicembre "
         f"{anno - 1}). Quando uscirà l'importo {anno + 1} aggiorneremo questa pagina."),
    ]
    jsonld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faq]}
    faq_html = "".join(domanda(escape(q), escape(t)) for q, t in faq)

    nota = ("Questa pagina spiega la regola e fa i conti, ma non è una consulenza legale. Decide lo Sportello unico per l'immigrazione della Prefettura: "
            "<strong>per il tuo caso chiedi allo Sportello unico o a un patronato.</strong>")
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Reddito per il ricongiungimento familiare", None))}
<span class="occhiello">{ic("euro")}Con le fonti ufficiali · {data_v}</span>
<h1>Reddito minimo per il ricongiungimento familiare {anno}</h1>
<p class="lead">{escape(risposta_breve)}</p>
<div class="risposta">
<div class="slot"><div class="r-et">{ic("euro")}Con 1 familiare</div>
<div class="r-data">{euro(uno[1])} <small>l'anno</small></div>
<div class="r-cosa">moglie, marito o 1 figlio · circa {euro(uno[2])} al mese su 12 mesi</div></div>
<div class="slot"><div class="r-et">{ic("lista")}Per ogni familiare in più</div>
<div class="r-data">+ {euro(meta)}</div>
<div class="r-cosa">è la metà dell'assegno sociale {anno} ({euro(annuo)} l'anno)</div>
<p class="r-nota">2 o più figli sotto i 14 anni: almeno {euro(doppio)} l'anno.</p></div>
<div class="r-piede"><a href="#tabella">Tabella per numero di familiari {ic("freccia")}</a><span>{ic("doc")}Fonti: INPS e Testo unico immigrazione</span></div>
</div>
</section>
{avviso(nota)}
<section>
<h2 id="tabella">{ic("euro")}Tabella {anno}: reddito minimo per numero di familiari</h2>
<p>Nella prima colonna conti solo i familiari che vuoi far venire in Italia. Nella seconda ci sei anche tu: per esempio «4 persone» sono tu, tua moglie e 2 figli, cioè 3 familiari da far venire.</p>
{tabella}
<p class="small">Per 6 o più familiari: {euro(annuo)} + {euro(meta)} per ogni familiare. La legge parla di reddito <strong>annuo</strong>: le colonne «al mese» sono solo un aiuto per confrontare con lo stipendio.</p>
</section>
<section>
<h2 id="calcolo">{ic("lista")}Come si calcola</h2>
<ol class="passi">
<li><div><strong>L'assegno sociale {anno} è {euro(mens)} al mese, per 13 mensilità: {euro(mens)} × 13 = {euro(annuo)} l'anno.</strong>
<p>L'importo annuo è nella tabella dell'INPS («Importi annui»), accanto a quello mensile. Nel {anno - 1} era {euro(Decimal(a["anno_precedente"]["mensile"]))} al mese, {euro(Decimal(a["anno_precedente"]["annuo"]))} l'anno.</p>
<div class="fonte">{ic("doc")}<span>Fonte: {fonte_inps}, {fonte_tab} · {verifica}</span></div></div></li>
<li><div><strong>Per ogni familiare si aggiunge la metà: {euro(meta)}.</strong>
<p>La legge chiede un reddito annuo «non inferiore all'importo annuo dell'assegno sociale aumentato della metà dell'importo dell'assegno sociale per ogni familiare da ricongiungere».</p>
<div class="fonte">{ic("doc")}<span>Fonte: {fonte_legge}, comma 3, lettera b) · {verifica}</span></div></div></li>
<li><div><strong>Esempio: moglie e 2 figli = 3 familiari: {euro(annuo)} + 3 × {euro(meta)} = {euro(tre[1])} l'anno.</strong>
<p>Al mese fa {euro(tre[2])} se dividi per 12 mesi, {euro(tre[3])} se dividi per 13 (per chi riceve anche la tredicesima).</p></div></li>
</ol>
<h3 id="figli-14">Due o più figli sotto i 14 anni</h3>
<p>La legge aggiunge: «per il ricongiungimento di due o più figli di età inferiore agli anni quattordici è richiesto, in ogni caso, un reddito non inferiore al doppio dell'importo annuo dell'assegno sociale».
Il doppio dell'assegno sociale {anno} è <strong>{euro(doppio)}</strong>. Se insieme ai figli arrivano altri familiari, o se i figli sono 3 o più, come si applicano le due regole lo decide lo Sportello unico: chiedi lì.</p>
<div class="fonte">{ic("doc")}<span>Fonte: {fonte_legge}, comma 3, lettera b) · {verifica}</span></div>
</section>
<section>
<h2 id="reddito">{ic("info")}Cosa conta come reddito</h2>
<p>La legge chiede un reddito annuo «derivante da fonti lecite» e dice che <strong>si somma anche il reddito dei familiari che vivono già con te</strong>
(«si tiene conto anche del reddito annuo complessivo dei familiari conviventi con il richiedente»). Quali documenti valgono per dimostrarlo, e di quale anno,
te lo dice lo Sportello unico della tua Prefettura.</p>
<div class="fonte">{ic("doc")}<span>Fonte: {fonte_legge}, comma 3, lettera b) · {verifica}</span></div>
</section>
<section>
<h2 id="chi">{ic("ok")}Chi puoi far venire</h2>
<p>Secondo il Ministero dell'Interno può chiedere il ricongiungimento chi è regolarmente in Italia con un <strong>permesso di soggiorno di almeno un anno</strong>, per:</p>
<ul>
<li>il coniuge maggiorenne, non separato legalmente;</li>
<li>i figli minorenni non sposati, con il consenso dell'altro genitore;</li>
<li>i figli maggiorenni a carico, per invalidità totale;</li>
<li>i genitori a carico, se non hanno altri figli nel Paese di origine, oppure con più di 65 anni se gli altri figli non possono mantenerli per gravi motivi di salute.</li>
</ul>
<div class="fonte">{ic("doc")}<span>Fonte: {fonte_sui} · {verifica}</span></div>
</section>
<section>
<h2 id="domanda">{ic("edificio")}Dove si fa la domanda</h2>
<p>La domanda di <strong>nulla osta al ricongiungimento</strong> si manda online allo <strong>Sportello unico per l'immigrazione</strong> della Prefettura della provincia dove vivi,
con i documenti su reddito e alloggio. Si compila sul <a href="{escape(sp["portale_url"])}" rel="noopener">Portale Servizi del Ministero dell'Interno</a>, con SPID o CIE.
Per legge il nulla osta va rilasciato entro 150 giorni dalla richiesta.</p>
<div class="fonte">{ic("doc")}<span>Fonti: {fonte_sui} · <a href="{escape(sp["portale_url"])}" rel="noopener">Portale Servizi – Sportello unico</a> · {fonte_legge}, commi 7 e 8 · {verifica}</span></div>
<h3 id="alloggio">Alloggio idoneo</h3>
<p>Oltre al reddito serve un <strong>alloggio</strong> che rispetti i requisiti igienico-sanitari e di idoneità abitativa, controllati dagli uffici del Comune
(contano anche quante persone ci vivranno). Per un figlio sotto i 14 anni che arriva con uno dei genitori basta il consenso di chi è titolare della casa dove abiterà.</p>
<div class="fonte">{ic("doc")}<span>Fonte: {fonte_legge}, comma 3, lettera a) · {verifica}</span></div>
<p class="small">Per chi ha lo status di rifugiato i requisiti di reddito e di alloggio non si applicano (<a href="{escape(r["url_29bis"])}" rel="noopener">art. 29-bis del Testo unico</a>).</p>
</section>
<section>
<h2 id="2027">{ic("cal")}Cosa cambia a gennaio {anno + 1}</h2>
<p>L'assegno sociale cambia ogni anno dal 1° gennaio, e con lui tutti gli importi di questa pagina. L'importo {anno} l'INPS l'ha pubblicato nella circolare del 19 dicembre {anno - 1}.
Quando uscirà l'importo {anno + 1} <strong>aggiorneremo la pagina</strong> con la nuova tabella. Quale anno conta per la tua domanda te lo dice lo Sportello unico.</p>
</section>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<div class="due">
<section>
<h2 id="esame">{ic("scudo")}E l'esame di italiano?</h2>
<p>Questa pagina riguarda il reddito per il ricongiungimento. Se un giorno chiederai la <strong>cittadinanza italiana</strong>, servirà un certificato di italiano
almeno B1 (con alcune esenzioni): <a href="../esonero-test-italiano/">chi è esonerato</a>, <a href="../#date">tutte le date d'esame</a>, <a href="../#citta">sedi per città</a>.</p>
</section>
<aside>{modulo()}</aside>
</div>"""
    titolo = titolo_pagina(f"Reddito ricongiungimento familiare {anno}: tabella")
    pagina("reddito-ricongiungimento-familiare/index.html", titolo,
           descrizione_pagina(f"Reddito minimo per il ricongiungimento familiare {anno}: {euro(uno[1])} l'anno con 1 familiare, + {euro(meta)} "
                              "per ogni familiare. Tabella da 1 a 5, fonti INPS."), corpo, jsonld)


# ---------------------------------------------------------------- redditi minimi (dal 31/10/2026)
REDDITI = json.loads((DATI / "redditi.json").read_text(encoding="utf-8"))  # soglie della cittadinanza e regola della carta di soggiorno, con fonti


def cent(x):
    """«8263.31» → 826331 centesimi (interi: Python e JS fanno gli stessi conti)."""
    return int((Decimal(str(x)) * 100).to_integral_value())


def euro_c(c):
    return euro(Decimal(c) / 100)


def calcola_redditi(coniuge, figli, reddito):
    """Confronto reddito/soglie, tutto in centesimi. coniuge: bool; figli: figli (o familiari) a carico; reddito: centesimi l'anno.
    Cittadinanza (Vademecum del Ministero): 8.263,31 da solo, 11.362,05 con coniuge a carico, + 516,00 per figlio o familiare a carico.
    Carta di soggiorno (art. 9 TU): assegno sociale annuo; per la richiesta anche per i familiari, + metà assegno per familiare (art. 29 c. 3 b).
    Stessa logica della funzione JS calcolaRedditi della pagina (controllo in raccolta/redditi.py)."""
    c = REDDITI["cittadinanza"]
    annuo = cent(RICONG["assegno_sociale"]["annuo"])
    familiari = (1 if coniuge else 0) + figli
    soglie = {"cittadinanza": cent(c["con_coniuge"] if coniuge else c["solo"]) + cent(c["per_figlio"]) * figli,
              "carta_solo": annuo, "carta_famiglia": annuo + annuo // 2 * familiari}
    return {k: {"soglia": v, "sopra": reddito >= v, "differenza": reddito - v} for k, v in soglie.items()} | {"familiari": familiari}


JS_REDDITI = """/*calcolo-inizio*/
function calcolaRedditi(coniuge, figli, reddito){
  var S=%s;
  var familiari=(coniuge?1:0)+figli;
  var soglie={cittadinanza:(coniuge?S.conCon:S.solo)+S.figlio*figli, carta_solo:S.annuo, carta_famiglia:S.annuo+Math.floor(S.annuo/2)*familiari};
  var r={};
  for(var k in soglie){r[k]={soglia:soglie[k],sopra:reddito>=soglie[k],differenza:reddito-soglie[k]};}
  r.familiari=familiari;
  return r;
}
/*calcolo-fine*/
(function(){
  var f=document.getElementById('calc-redditi');if(!f)return;
  function eur(c){var n=Math.abs(c),e=Math.floor(n/100),d=String(n%%100).padStart(2,'0');return e.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.')+','+d+' \\u20ac';}
  function leggiEuro(t){t=String(t||'').replace(/[\\s\\u20ac]/g,'');if(!t)return null;
    if(/,\\d{1,2}$/.test(t)){t=t.replace(/\\./g,'').replace(',','.');}else if(/\\.\\d{1,2}$/.test(t)&&t.split('.').length===2){}else{t=t.replace(/[.,]/g,'');}
    var v=Number(t);return isFinite(v)&&v>=0?Math.round(v*100):null;}
  var out=document.getElementById('calc-esito');
  function riga(id,titolo,x,chi){var el=out.querySelector('[data-r="'+id+'"]');if(!el)return;
    el.hidden=false;el.className='c-riga '+(x.sopra?'si':'no');
    el.querySelector('.c-tit').textContent=titolo;
    el.querySelector('.c-soglia').textContent='Soglia: '+eur(x.soglia)+' l\\u2019anno';
    el.querySelector('.c-esito').textContent=x.sopra?('Sei sopra la soglia di '+eur(x.differenza)+'.'):('Sei sotto la soglia: mancano '+eur(-x.differenza)+'.');
    el.querySelector('.c-chi').textContent=chi;}
  function calcola(ev){if(ev)ev.preventDefault();
    var coniuge=f.coniuge.checked,figli=Math.max(0,Math.min(20,parseInt(f.figli.value,10)||0));
    var reddito=leggiEuro(f.reddito.value),err=f.querySelector('[data-errore]');
    if(reddito===null){err.hidden=false;out.hidden=true;return;}
    err.hidden=true;out.hidden=false;
    var r=calcolaRedditi(coniuge,figli,reddito);
    riga('cittadinanza','Cittadinanza italiana per residenza',r.cittadinanza,'Decide la Prefettura: guarda il reddito imponibile IRPEF degli ultimi 3 anni.');
    riga('carta_solo','Carta di soggiorno (permesso UE di lungo periodo), solo per te',r.carta_solo,'Decide la Questura.');
    var fam=out.querySelector('[data-r="carta_famiglia"]');
    if(r.familiari>0){riga('carta_famiglia','Carta di soggiorno anche per '+(r.familiari===1?'1 familiare':r.familiari+' familiari'),r.carta_famiglia,'Decide la Questura.');}else{fam.hidden=true;}
    out.querySelector('[data-quattordici]').hidden=figli<2;
  }
  f.addEventListener('submit',calcola);
  f.addEventListener('change',function(){if(f.reddito.value)calcola();});
})();"""


def pagina_redditi():
    """Redditi minimi per stranieri: cittadinanza per residenza (soglie del Ministero) e carta di soggiorno (assegno sociale), con calcolatore.
    Il ricongiungimento ha la sua pagina: qui solo il collegamento. Nessun riquadro «Preparati»: la pagina non riguarda l'esame."""
    c, ca = REDDITI["cittadinanza"], REDDITI["carta_soggiorno"]
    F = {**c["fonti"], **ca["fonti"]}
    a = RICONG["assegno_sociale"]
    anno = RICONG["anno"]
    solo, con, fig = cent(c["solo"]), cent(c["con_coniuge"]), cent(c["per_figlio"])
    annuo = cent(a["annuo"])
    meta = annuo // 2
    data_v = data_breve(min(f["verificato_il"] for f in F.values()))

    def fonte(*chiavi, extra=""):
        link = " · ".join(f'<a href="{escape(F[k]["url"])}" rel="noopener">{escape(F[k]["breve"])}</a>' for k in chiavi)
        return f'<div class="fonte">{ic("doc")}<span>Fonte: {link}{extra} · controllato il {data_breve(max(F[k]["verificato_il"] for k in chiavi))}</span></div>'

    fonte_inps = (f' · assegno sociale {anno}: <a href="{escape(a["url"])}" rel="noopener">INPS, circolare n. 153 del 19/12/2025</a> '
                  f'(<a href="{escape(a["url_allegato"])}" rel="noopener">tabella A</a>)')
    # tabella cittadinanza: 0-4 figli, da solo / con coniuge (stessi numeri del PDF della Prefettura, controllati in redditi.py)
    righe_c = "".join(
        f'<tr><td><strong>{n} {"figlio" if n == 1 else "figli"} a carico</strong></td>'
        f'<td data-l="Senza coniuge">{euro_c(calcola_redditi(False, n, 0)["cittadinanza"]["soglia"])}</td>'
        f'<td data-l="Con coniuge a carico">{euro_c(calcola_redditi(True, n, 0)["cittadinanza"]["soglia"])}</td></tr>' for n in range(0, 5))
    tab_c = (f'<div class="tab-wrap rc-tab"><table class="conf"><caption class="small">Reddito imponibile minimo all\'anno per la cittadinanza per residenza</caption>'
             '<thead><tr><th scope="col">Figli (o altri familiari) a carico</th><th scope="col">Senza coniuge</th><th scope="col">Con coniuge a carico</th></tr></thead>'
             f'<tbody>{righe_c}</tbody></table></div>')
    righe_k = "".join(
        f'<tr><td><strong>{"solo per te" if n == 0 else ("te e 1 familiare" if n == 1 else f"te e {n} familiari")}</strong></td>'
        f'<td data-l="Persone">{n + 1} {"persona" if n == 0 else "persone"}</td><td data-l="All\'anno"><strong>{euro_c(annuo + meta * n)}</strong></td>'
        f'<td data-l="Al mese, su 12">{euro_c(round((annuo + meta * n) / 12))}</td></tr>' for n in range(0, 6))
    tab_k = (f'<div class="tab-wrap rc-tab"><table class="conf"><caption class="small">Reddito minimo {anno} per la carta di soggiorno (permesso UE di lungo periodo)</caption>'
             '<thead><tr><th scope="col">Per chi chiedi la carta</th><th scope="col">Persone</th><th scope="col">Reddito minimo all\'anno</th><th scope="col">Al mese, su 12 mesi</th></tr></thead>'
             f'<tbody>{righe_k}</tbody></table></div>')
    ex3a, ex3b = calcola_redditi(True, 1, 0)["cittadinanza"]["soglia"], calcola_redditi(False, 2, 0)["cittadinanza"]["soglia"]
    ex4a = calcola_redditi(True, 2, 0)["cittadinanza"]["soglia"]
    js_soglie = json.dumps({"solo": solo, "conCon": con, "figlio": fig, "annuo": annuo})
    faq = [
        (f"Qual è il reddito minimo per la cittadinanza italiana nel {anno}?",
         f"Per la cittadinanza per residenza servono almeno {euro_c(solo)} l'anno di reddito imponibile se sei solo, {euro_c(con)} con il coniuge a carico, "
         f"più {euro_c(fig)} per ogni figlio o familiare a carico. Sono le soglie scritte dal Ministero dell'Interno nel Vademecum del 23 aprile 2025; "
         "non cambiano ogni anno."),
        ("Il reddito per la cittadinanza è lordo o netto?",
         "Conta il reddito imponibile IRPEF dichiarato in Italia. Per il modello 730 è il «Reddito imponibile» nel Prospetto di liquidazione, come scrive la Prefettura. "
         "Non è lo stipendio netto in busta paga."),
        ("Quanto reddito serve per la cittadinanza per 3 o 4 persone?",
         f"3 persone: con coniuge e 1 figlio a carico {euro_c(ex3a)}, oppure da solo con 2 figli a carico {euro_c(ex3b)}. "
         f"4 persone (tu, coniuge e 2 figli a carico): {euro_c(ex4a)}. Sono importi all'anno."),
        ("Conta il reddito del coniuge o del convivente?",
         "Sì per il coniuge, la parte unita civilmente e gli altri familiari dell'art. 433 del Codice civile. "
         "Il Vademecum del Ministero dice che non conta il reddito del convivente senza un legame giuridico, anche con figli, né quello del coniuge che vive all'estero. "
         "Conta invece il convivente con un contratto di convivenza."),
        ("Cosa succede se il reddito della cittadinanza è insufficiente in un anno?",
         "Secondo il Vademecum la Prefettura può valutare «in via equitativa» un calo di reddito in un solo anno o seguito da un lavoro stabile. "
         "La domanda con reddito sotto le soglie, invece, può essere rifiutata subito online. Il reddito va mantenuto fino al giuramento."),
        (f"Quanto reddito serve per la carta di soggiorno nel {anno}?",
         f"Almeno l'assegno sociale {anno}: {euro_c(annuo)} l'anno solo per te. Se chiedi la carta anche per i familiari si aggiunge la metà "
         f"({euro_c(meta)}) per ognuno: per 4 persone (tu e 3 familiari) {euro_c(annuo + meta * 3)}. Decide la Questura."),
        ("Le soglie cambiano nel 2027?",
         f"Quelle della cittadinanza no: sono fisse in euro dal 1995. Quelle della carta di soggiorno sì, perché seguono l'assegno sociale, che l'INPS aggiorna ogni gennaio: "
         "aggiorneremo la pagina con il nuovo importo."),
    ]
    faq_html = "".join(domanda(escape(q), escape(t)) for q, t in faq)
    jsonld = {"@context": "https://schema.org"} | faq_jsonld([(escape(q), escape(t)) for q, t in faq])
    lead = (f"Per la cittadinanza italiana per residenza serve un reddito imponibile di almeno {euro_c(solo)} l'anno se sei solo, {euro_c(con)} con il coniuge a carico "
            f"e {euro_c(fig)} in più per ogni figlio a carico: lo scrive il Ministero dell'Interno nel Vademecum del 23 aprile 2025 (letto il {data_v}). "
            f"Per la carta di soggiorno serve almeno l'assegno sociale {anno}, {euro_c(annuo)} l'anno (art. 9 del Testo unico immigrazione).")
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Redditi minimi per stranieri", None))}
<span class="occhiello">{ic("euro")}Con le fonti ufficiali · {data_v}</span>
<h1>Reddito minimo per la cittadinanza italiana e la carta di soggiorno {anno}</h1>
<p class="lead">{escape(lead)}</p>
<div class="risposta">
<div class="slot"><div class="r-et">{ic("scudo")}Cittadinanza (Prefettura)</div>
<div class="r-data">{euro_c(solo)} <small>l'anno</small></div>
<div class="r-cosa">da solo · {euro_c(con)} con coniuge a carico · + {euro_c(fig)} per figlio</div></div>
<div class="slot"><div class="r-et">{ic("doc")}Carta di soggiorno (Questura)</div>
<div class="r-data">{euro_c(annuo)} <small>l'anno</small></div>
<div class="r-cosa">solo per te · + {euro_c(meta)} per ogni familiare</div></div>
<div class="r-piede"><a href="#calcola">Fai il conto con la tua famiglia {ic("freccia")}</a><span>{ic("doc")}Fonti: Ministero dell'Interno, Prefettura, Testo unico, INPS</span></div>
</div>
</section>
{avviso("Questa pagina confronta il tuo reddito con le soglie ufficiali, ma non è una consulenza. <strong>Per la cittadinanza decide la Prefettura, per la carta di soggiorno decide la Questura.</strong> Per il tuo caso chiedi a loro o a un patronato.")}
<section>
<h2 id="calcola">{ic("lista")}Calcola: sei sopra o sotto le soglie?</h2>
<form class="form calc card" id="calc-redditi" novalidate>
<label class="check"><input type="checkbox" name="coniuge"><span>Ho il coniuge (o la parte unita civilmente) fiscalmente a carico</span></label>
<p class="small">Se il coniuge ha un suo reddito e non è a carico, non spuntare la casella: il suo reddito imponibile si somma al tuo nel campo qui sotto (la soglia più alta vale solo «in presenza del coniuge a carico», scrive il Vademecum).</p>
<label>Figli (o altri familiari) a carico<input type="number" name="figli" min="0" max="20" value="0" inputmode="numeric"></label>
<label>Reddito imponibile della famiglia all'anno, in euro<input type="text" name="reddito" inputmode="decimal" placeholder="per esempio 12.500" autocomplete="off"></label>
<button class="btn" type="submit">{ic("euro")}Confronta con le soglie</button>
<p class="errore" data-errore hidden>Scrivi il reddito in euro, per esempio 12.500 o 12500,50.</p>
</form>
<div class="calc-esito" id="calc-esito" aria-live="polite" hidden>
<div data-r="cittadinanza" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<div data-r="carta_solo" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<div data-r="carta_famiglia" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<p class="small" data-quattordici hidden>Con 2 o più figli sotto i 14 anni, per il ricongiungimento la legge chiede almeno {euro_c(annuo * 2)} l'anno: per la carta di soggiorno chiedi alla Questura se vale anche per te.</p>
<p class="small">Il calcolo usa solo le soglie ufficiali. Non sa se il tuo reddito è «imponibile», di quali anni è, né se i documenti vanno bene: <strong>decide la Prefettura (cittadinanza) o la Questura (carta di soggiorno)</strong>. Per far venire i familiari in Italia guarda il <a href="../reddito-ricongiungimento-familiare/">reddito per il ricongiungimento</a>.</p>
</div>
<p class="small">Il calcolo resta nel tuo browser: non salviamo nulla.</p>
</section>
<section>
<h2 id="cittadinanza">{ic("scudo")}Cittadinanza per residenza: quanto reddito serve</h2>
<p>Il Ministero dell'Interno usa come soglia i limiti di reddito per l'esenzione dal ticket sanitario dei pensionati: <strong>{euro_c(solo)}</strong> per chi è solo,
<strong>{euro_c(con)}</strong> con il coniuge a carico e <strong>{euro_c(fig)} in più</strong> per ogni figlio o familiare a carico ({escape(c["norma"])}).</p>
{fonte("vademecum", "pdf_prefettura")}
{tab_c}
<p class="small">Per 5 o più figli: aggiungi {euro_c(fig)} per ogni figlio. I numeri della tabella sono gli stessi del PDF della Prefettura.</p>
<h3 id="quale-reddito">Quale reddito conta: lordo o netto?</h3>
<p>Contano <strong>solo i redditi imponibili IRPEF dichiarati in Italia</strong> negli <strong>ultimi 3 anni</strong>; quelli all'estero non contano. Nel modello 730 è il «Reddito imponibile» del Prospetto di liquidazione;
nel modello Redditi PF e nella Certificazione Unica la Prefettura spiega quali righe sommare. Nella domanda si scrivono i codici ricevuta delle dichiarazioni.</p>
{fonte("pdf_prefettura", "vademecum")}
<h3 id="famiglia">Il reddito della famiglia</h3>
<p>Si può sommare il reddito dei familiari dell'art. 433 del Codice civile che sono nello stato di famiglia: coniuge (o parte unita civilmente, o convivente con contratto scritto di convivenza), figli, genitori, generi e nuore, suoceri, fratelli e sorelle.
<strong>Non contano</strong>, secondo il Vademecum: il convivente senza legame giuridico (anche con figli in comune), il patrigno o la matrigna, il coniuge che vive all'estero.</p>
{fonte("vademecum", "pdf_prefettura")}
<h3 id="non-conta">Cosa non conta come reddito</h3>
<ul>
<li>il reddito o la pensione di cittadinanza;</li>
<li>i soldi sul conto corrente;</li>
<li>la pensione presa e tassata all'estero;</li>
<li>la disoccupazione (NASpI), anche se è tassata.</li>
</ul>
<p>Contano invece, tra gli altri: lavoro, pensioni italiane (anche di invalidità), rendite INAIL continuative, redditi della parte unita civilmente.</p>
{fonte("vademecum")}
<h3 id="anni">Se un anno è andato male</h3>
<p>Se il reddito scende in un solo anno, o poi arriva un lavoro stabile, il Vademecum dice che la Prefettura può valutare il calo «in via equitativa». Ma se il reddito dichiarato è sotto le soglie la domanda può essere <strong>rifiutata subito online</strong>,
e il reddito va <strong>mantenuto fino al giuramento</strong>: la Prefettura lo ricontrolla prima del decreto.</p>
{fonte("vademecum", "pdf_prefettura")}
</section>
<section>
<h2 id="carta-di-soggiorno">{ic("doc")}Carta di soggiorno (permesso UE di lungo periodo): quanto reddito serve</h2>
<p>La legge chiede almeno <strong>5 anni</strong> di permesso di soggiorno e un reddito <strong>non inferiore all'assegno sociale</strong>: nel {anno} sono <strong>{euro_c(annuo)} l'anno</strong>.
Se chiedi la carta anche per i familiari, il reddito deve seguire le regole del ricongiungimento: assegno sociale <strong>+ {euro_c(meta)} per ogni familiare</strong>. Serve anche un alloggio idoneo.</p>
{fonte("tu9", extra=fonte_inps)}
{tab_k}
<p class="small">«Al mese» è solo un aiuto per confrontare: la legge parla di reddito annuo. Quali documenti e quale reddito valgono lo decide la Questura. Per la carta serve anche il test di italiano A2, con alcune esenzioni: <a href="../esonero-test-italiano/">chi è esonerato</a>.</p>
</section>
<section>
<h2 id="ricongiungimento">{ic("pin")}Ricongiungimento familiare</h2>
<p>Per far venire in Italia moglie, marito, figli o genitori il reddito minimo segue l'assegno sociale, con una regola speciale per 2 o più figli sotto i 14 anni. Tabella, calcolo e fonti sono in una pagina a parte.</p>
<div class="griglia link3"><a href="../reddito-ricongiungimento-familiare/">{ic("euro")}<span>Reddito per il ricongiungimento familiare {anno}<small>tabella da 1 a 5 familiari</small></span></a>
<a href="../cittadinanza/">{ic("edificio")}<span>Domanda di cittadinanza, prefettura per prefettura<small>ufficio, contatti, contributo di 250 €</small></span></a>
<a href="../esonero-test-italiano/">{ic("scudo")}<span>Chi è esonerato dal B1 e dal test A2<small>con le fonti</small></span></a></div>
</section>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<div class="due">
<section>
<h2 id="esame">{ic("cal")}E l'esame di italiano?</h2>
<p>Per la cittadinanza per residenza serve anche un certificato di italiano almeno B1 (con alcune esenzioni). Trovi <a href="../#date">tutte le date d'esame</a>, le <a href="../#citta">sedi per città</a>
e <a href="../cittadinanza/">come si presenta la domanda nella tua Prefettura</a>.</p>
</section>
<aside>{modulo()}</aside>
</div>
<script>{JS_REDDITI % js_soglie}</script>"""
    titolo = titolo_pagina(f"Reddito minimo cittadinanza italiana {anno}: tabella e calcolo",
                           f"Reddito minimo cittadinanza {anno}: tabella e calcolo")
    descr = descrizione_pagina(
        f"Reddito minimo per la cittadinanza italiana {anno}: {euro_c(solo)} da solo, {euro_c(con)} con coniuge, + {euro_c(fig)} per figlio. "
        f"Carta di soggiorno: {euro_c(annuo)}. Calcolatore.",
        f"Reddito minimo cittadinanza {anno}: {euro_c(solo)} da solo, {euro_c(con)} con coniuge, + {euro_c(fig)} per figlio. Carta di soggiorno {euro_c(annuo)}.")
    pagina("reddito-minimo-cittadinanza/index.html", titolo, descr, corpo, jsonld)


# ---------------------------------------------------------------- domanda di cittadinanza, prefettura per prefettura (dal 31/10/2026)
PREF = {r["slug"]: r for r in json.loads((DATI / "prefetture.json").read_text(encoding="utf-8"))["prefetture"]}  # raccolta/prefetture.py
PREF_LOC = json.loads((DATI / "prefetture_locali.json").read_text(encoding="utf-8"))  # punti locali scelti a mano, con la frase esatta
CITT = json.loads((DATI / "cittadinanza.json").read_text(encoding="utf-8"))  # dati nazionali (Ministero), con fonti
SIGLE = {"agrigento": "ag", "alessandria": "al", "ancona": "an", "aosta": "ao", "arezzo": "ar", "ascoli-piceno": "ap", "asti": "at", "avellino": "av",
         "bari": "ba", "barletta-andria-trani": "bt", "belluno": "bl", "benevento": "bn", "bergamo": "bg", "biella": "bi", "bologna": "bo", "bolzano": "bz",
         "brescia": "bs", "brindisi": "br", "cagliari": "ca", "caltanissetta": "cl", "campobasso": "cb", "caserta": "ce", "catania": "ct", "catanzaro": "cz",
         "chieti": "ch", "como": "co", "cosenza": "cs", "cremona": "cr", "crotone": "kr", "cuneo": "cn", "enna": "en", "fermo": "fm", "ferrara": "fe",
         "firenze": "fi", "foggia": "fg", "forli-cesena": "fc", "frosinone": "fr", "genova": "ge", "gorizia": "go", "grosseto": "gr", "imperia": "im",
         "isernia": "is", "laquila": "aq", "latina": "lt", "lecce": "le", "lecco": "lc", "livorno": "li", "lodi": "lo", "lucca": "lu", "macerata": "mc",
         "mantova": "mn", "massa-carrara": "ms", "matera": "mt", "messina": "me", "milano": "mi", "modena": "mo", "monza-e-brianza": "mb", "napoli": "na",
         "novara": "no", "nuoro": "nu", "oristano": "or", "padova": "pd", "palermo": "pa", "parma": "pr", "pavia": "pv", "perugia": "pg", "pesaro-urbino": "pu",
         "pescara": "pe", "piacenza": "pc", "pisa": "pi", "pistoia": "pt", "pordenone": "pn", "potenza": "pz", "prato": "po", "ragusa": "rg", "ravenna": "ra",
         "reggio-calabria": "rc", "reggio-emilia": "re", "rieti": "ri", "rimini": "rn", "roma": "rm", "rovigo": "ro", "salerno": "sa", "sassari": "ss",
         "savona": "sv", "siena": "si", "siracusa": "sr", "sondrio": "so", "spezia": "sp", "taranto": "ta", "teramo": "te", "terni": "tr", "torino": "to",
         "trapani": "tp", "trento": "tn", "treviso": "tv", "trieste": "ts", "udine": "ud", "varese": "va", "venezia": "ve", "verbano-cusio-ossola": "vb",
         "vercelli": "vc", "verona": "vr", "vibo-valentia": "vv", "vicenza": "vi", "viterbo": "vt"}
URL_PREF = {"laquila": "l-aquila", "spezia": "la-spezia"}  # indirizzo della nostra pagina, se diverso dallo slug del Ministero
PROV_PREF = {"Monza e della Brianza": "monza-e-brianza", "Reggio nell'Emilia": "reggio-emilia", "Pesaro e Urbino": "pesaro-urbino",
             "La Spezia": "spezia", "L'Aquila": "laquila"}


def pref_url(sl):
    return URL_PREF.get(sl, sl)


def pref_di(provincia):
    """Slug della prefettura per la provincia scritta in citta.json/sedi.json ("Bolzano/Bozen" → "bolzano")."""
    sl = PROV_PREF.get(provincia, slug(provincia))
    return sl if sl in PREF else None


def ha_pagina_pref(sl):
    return sl in PREF_LOC["prefetture"] and len(PREF_LOC["prefetture"][sl].get("punti", [])) >= 2


def caselle_proprie(sl):
    """Caselle scritte sulla pagina della Prefettura che sono sue (nome o sigla della provincia nell'indirizzo): niente caselle di altre prefetture
    copiate per errore, niente caselle del Ministero (quelle nazionali sono nella pagina indice)."""
    r = PREF[sl]
    nome = re.sub(r"[^a-z]", "", norma_luogo(r["nome"]))
    tutte = [m for v in r.get("rubrica", {}).values() for m in re.findall(r"[\w.+-]+@[\w.-]+", v)] + r.get("email_testo", [])
    proprie = []
    for m in dict.fromkeys(x.lower() for x in tutte):
        loc = m.split("@")[0].replace("_", "").replace("-", "").replace(".", "")
        if "pecdlci" in m or loc.startswith(("depenalizzazione", "sanzioni", "patenti", "elettorale", "antimafia", "contenzioso")):
            continue  # caselle del Ministero o di altri uffici della Prefettura (non la cittadinanza)
        if nome[:6] in loc or loc.endswith("pref" + SIGLE[sl]) or loc.endswith("comgov" + SIGLE[sl]):
            proprie.append(m)
    return proprie


def data_it(testo):
    """«Martedì 22 Settembre 2026, ore 08:50» → «22 settembre 2026» (vuoto se non si legge)."""
    m = re.search(r"(\d{1,2}) (\w+) (\d{4})", testo or "")
    if not m or m.group(2).lower() not in MESI:
        return ""
    return f"{int(m.group(1))} {m.group(2).lower()} {m.group(3)}"


def fonte_citt(*chiavi):
    F = CITT["fonti"]
    link = " · ".join(f'<a href="{escape(F[k]["url"])}" rel="noopener">{escape(F[k]["nome"])}</a>' for k in chiavi)
    return f'<div class="fonte">{ic("doc")}<span>Fonte: {link} · controllato il {data_breve(max(F[k]["verificato_il"] for k in chiavi))}</span></div>'


def come_domanda(rel):
    """Come si presenta la domanda, in breve (dati nazionali del Ministero): uguale per tutte le prefetture, quindi corto e con link all'indice."""
    F = CITT["fonti"]
    return f"""<ol class="passi">
<li><div><strong>Domanda solo online</strong>, sul <a href="{escape(F["portale"]["url"])}" rel="noopener">Portale Servizi del Ministero dell'Interno</a> (ALI Cittadinanza), con <strong>SPID o CIE</strong>.</div></li>
<li><div><strong>Documenti da allegare</strong>: documento di riconoscimento, atto di nascita e certificato penale del Paese di origine, certificato di italiano almeno <a href="{rel}#date">B1</a> (salvo <a href="{rel}esonero-test-italiano/">esoneri</a>), ricevuta del contributo, estremi della marca da bollo telematica.</div></li>
<li><div><strong>Contributo di {CITT["contributo_eur"]} €</strong>: si allega la ricevuta del pagamento.</div></li>
<li><div><strong>Reddito</strong>: servono almeno le <a href="{rel}reddito-minimo-cittadinanza/">soglie del Ministero</a> negli ultimi 3 anni (per residenza).</div></li>
<li><div><strong>Dopo l'invio</strong>: la pratica ha un numero K10; lo stato si vede online con le stesse credenziali.</div></li>
</ol>
{fonte_citt("domanda", "consulta")}"""


# Indirizzi scritti dalle Prefetture che il 31/10/2026 non rispondevano dal server (nessuna risposta, non un rifiuto):
# si mostrano come testo, non come link. Ricontrollare e togliere da qui quando rispondono.
NON_RAGGIUNGIBILI = {"http://www.utgvenezia.it/booking/", "https://prenotazioni.utgroma.it/"}
TIPI_CONTATTO = {"email": ("mail", "Email"), "pec": ("mail", "PEC"), "telefono": ("tel", "Telefono"), "orari": ("orologio", "Orari"),
                 "ricevimento": ("orologio", "Ricevimento"), "indirizzo": ("pin", "Indirizzo"), "prenotazione": ("cal", "Prenotazione")}


def contatti_di(sl):
    """[(tipo, valore, nota)]: scelti a mano (con la frase esatta) se ci sono, altrimenti i campi d'ufficio raccolti dalla pagina."""
    loc = PREF_LOC["prefetture"].get(sl, {})
    if loc.get("contatti"):
        return [(c["tipo"], c["valore"], c.get("nota", "")) for c in loc["contatti"]]
    rub = PREF[sl].get("rubrica", {})
    out = [(t, rub[k], "") for k, t in (("Ricevimento", "ricevimento"), ("Orari", "orari"), ("Telefoni", "telefono"), ("Telefono", "telefono"),
                                         ("Ubicazione", "indirizzo")) if rub.get(k)]
    return out + [("pec" if "pec" in m.split("@")[1] else "email", m, "") for m in caselle_proprie(sl)]


def contatti_pref(sl):
    html_r = []
    for tipo, val, nota in contatti_di(sl):
        icona, et = TIPI_CONTATTO[tipo]
        if tipo in ("email", "pec"):
            v = f'<a href="mailto:{escape(val)}">{escape(val)}</a>'
        elif tipo == "prenotazione" and val.startswith("http") and val not in NON_RAGGIUNGIBILI:
            v = f'<a href="{escape(val)}" rel="noopener">{escape(val)}</a>'
        else:
            v = escape(val)
        html_r.append(f'<li>{ic(icona)}<span><b>{et}:</b> {v}{f" <span class=small>({escape(nota)})</span>" if nota else ""}</span></li>')
    return "".join(html_r)


def faq_prefettura(sl):
    """Domande frequenti della pagina prefettura: quelle cercate su Google («prefettura X cittadinanza pec / telefono / orari»),
    con le risposte prese solo dai contatti scritti dalla Prefettura; più quelle scelte a mano in prefetture_locali.json."""
    nome = PREF[sl]["nome"]
    cc = contatti_di(sl)
    def di_tipo(*tipi):
        return [(v, n) for t, v, n in cc if t in tipi]
    fonte = f"(pagina «Cittadinanza» della Prefettura di {nome}, letta il {data_breve(PREF[sl]['letto_il'])})"
    pec, mail, tel, ore = di_tipo("pec"), di_tipo("email"), di_tipo("telefono"), di_tipo("orari", "ricevimento")
    faq = []
    if pec:
        faq.append((f"Qual è la PEC dell'ufficio cittadinanza della Prefettura di {nome}?",
                    "; ".join(f"{v}" + (f" ({n})" if n else "") for v, n in pec) + f" {fonte}. Scrivi sempre il numero K10 della pratica nell'oggetto."))
    else:
        faq.append((f"Qual è la PEC dell'ufficio cittadinanza della Prefettura di {nome}?",
                    f"La pagina della Prefettura non indica una PEC propria per la cittadinanza. Il Ministero indica {CITT['pec_ministero']}, con il numero K10 nell'oggetto."))
    if mail:
        faq.append((f"Qual è l'email dell'ufficio cittadinanza di {nome}?", "; ".join(v + (f" ({n})" if n else "") for v, n in mail) + f" {fonte}."))
    faq.append((f"Qual è il telefono dell'ufficio cittadinanza della Prefettura di {nome}?",
                ("; ".join(v + (f" ({n})" if n else "") for v, n in tel) + f" {fonte}.") if tel else
                f"La pagina della Prefettura non scrive un numero di telefono per la cittadinanza. C'è il Polo Orienta del Ministero: {CITT['polo_orienta']['telefono']}, {CITT['polo_orienta']['giorni']}."))
    if ore:
        faq.append((f"Quali sono gli orari dell'ufficio cittadinanza di {nome}? Serve l'appuntamento?", "; ".join(v + (f" ({n})" if n else "") for v, n in ore) + f" {fonte}."))
    faq.append((f"Come si presenta la domanda di cittadinanza a {nome}?",
                f"Online, sul Portale Servizi del Ministero dell'Interno, con SPID o CIE, come in tutta Italia; la segue la Prefettura di {nome}. "
                f"Si allegano documento, atto di nascita, certificato penale, certificato B1 (salvo esoneri) e la ricevuta del contributo di {CITT['contributo_eur']} €."))
    return faq + [tuple(x) for x in PREF_LOC["prefetture"].get(sl, {}).get("faq", [])]


def nome_file(t):
    t = re.sub(r"\.(pdf|docx?|rtf|odt)$", "", t.strip(), flags=re.I).replace("_", " ").replace("-", " ").strip()
    return (t[:1].upper() + t[1:]) if t else "Allegato"


def citta_della_pref(sl):
    return [c for c in citta if pref_di(c["provincia"]) == sl]


def pagina_prefettura(sl, prossime):
    r, loc = PREF[sl], PREF_LOC["prefetture"][sl]
    nome = r["nome"]
    di = f"di {nome}"
    agg = data_it(r.get("ultimo_aggiornamento", ""))
    letto = data_breve(r["letto_il"])
    url = r["url"]
    fonte_pref = (f'<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(url)}" rel="noopener">Prefettura {escape(di)}, pagina «Cittadinanza»</a>'
                  f'{f" (aggiornata il {agg})" if agg else ""} · letta il {letto}</span></div>')
    punti = []
    for pnt in loc["punti"]:
        u = pnt.get("url") or url
        nome_fonte = pnt.get("fonte") or "pagina «Cittadinanza»"
        cit = "".join(f'<p class="citaz">«{escape(c)}»</p>' for c in pnt["citazioni"][:1])
        punti.append(f'<div class="fatto"><div class="f-et">{ic(pnt.get("icona", "info"))}<span>{escape(pnt["titolo"])}</span></div><p>{pnt["testo"]}</p>{cit}'
                     f'<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(u)}" rel="noopener">Prefettura {escape(di)}, {escape(nome_fonte)}</a> · letta il {letto}</span></div></div>')
    allegati = "".join(f'<li>{ic("doc")}<a href="{escape(a["url"])}" rel="noopener">{escape(nome_file(a["titolo"]))}</a></li>'
                       for a in r.get("allegati", []) if a["titolo"].strip() and a.get("stato") == 200)  # solo i file che rispondono 200
    cc = citta_della_pref(sl)
    sedi_prov = [s for s in sedi if pref_di(s["provincia"]) == sl]
    if cc:
        esame = (f"In provincia {di} ci sono <strong>{n_sedi(len(sedi_prov))}</strong> dove fare l'esame B1 per la cittadinanza: "
                 + ", ".join(f'<a href="../../citta/{c["slug"]}/">esame B1 {a_(c)}</a>' for c in cc) + ".")
    else:
        esame = f'Trovi date e sedi dell\'esame B1 nella <a href="../../#citta">pagina delle città</a>.'
    p = prossima_di(prossime)
    contatti = contatti_pref(sl)
    faq = faq_prefettura(sl)
    faq_html = "".join(domanda(escape(q), escape(t)) for q, t in faq)
    lead = (f'Secondo la <a href="{escape(url)}" rel="noopener">pagina «Cittadinanza» della Prefettura {escape(di)}</a>'
            f'{f" (aggiornata il {agg}, letta il {letto})" if agg else f" (letta il {letto})"}, {loc["lead"]}')
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), ("Cittadinanza", "../"), (nome, None))}
<span class="occhiello">{ic("edificio")}Prefettura {escape(di)} · letta il {letto}</span>
<h1>Domanda di cittadinanza a {escape(nome)}: cosa dice la Prefettura</h1>
<p class="lead">{lead}</p>
</section>
{avviso(f"Qui trovi solo quello che scrive la Prefettura {escape(di)} sulla sua pagina, con la data di lettura. <strong>Decide la Prefettura</strong>: per il tuo caso scrivi all'ufficio o chiedi a un patronato. Questo sito non è della Prefettura.")}
<section>
<h2 id="contatti">{ic("mail")}Ufficio cittadinanza: contatti</h2>
{f'<ul class="uff">{contatti}</ul>' if contatti else f'<p>La pagina della Prefettura non indica contatti specifici dell\'ufficio: usa la <a href="{escape(url)}" rel="noopener">pagina ufficiale</a>.</p>'}
{f'<p class="small">{loc["nota_contatti"]}</p>' if loc.get("nota_contatti") else ""}
{fonte_pref}
<div class="azioni"><a class="btn btn-2" href="{escape(url)}" rel="noopener">{ic("web")}Pagina «Cittadinanza» della Prefettura {escape(di)} {ic("freccia")}</a></div>
</section>
<section>
<h2 id="locale">{ic("info")}Cosa scrive la Prefettura {escape(di)}</h2>
<div class="fatti locali">{"".join(punti)}</div>
{f'<h3 id="moduli">Moduli e documenti sulla pagina della Prefettura</h3><ul class="uff">{allegati}</ul>' if allegati else ""}
</section>
<section>
<h2 id="domanda">{ic("lista")}Come si presenta la domanda (uguale in tutta Italia)</h2>
{come_domanda("../../")}
<p class="small">Più dettagli, tempi e contatti nazionali: <a href="../#come">domanda di cittadinanza, la guida</a>.</p>
</section>
<section>
<h2 id="esame">{ic("cal")}Prima della domanda: l'esame B1</h2>
<p>{esame}{f" Prossimo esame: {data_lunga(p['data'])} ({escape(p['ente'])})." if p else ""}</p>
</section>
{f'<section><h2>{ic("info")}Domande frequenti</h2>{faq_html}</section>' if faq else ""}
<section>
<h2>{ic("pin")}Altre prefetture</h2>
<div class="altre">{"".join(f'<a href="../{pref_url(x)}/">{escape(PREF[x]["nome"])}</a>' for x in sorted(PREF, key=lambda x: PREF[x]["nome"]) if x != sl and ha_pagina_pref(x) and PREF[x]["regione"] == r["regione"])}<a href="../#elenco">Tutte le 106 prefetture</a></div>
</section>"""
    jsonld = {"@context": "https://schema.org"} | faq_jsonld([(escape(q), escape(t)) for q, t in faq]) if faq else None
    tipi = {t for t, _, _ in contatti_di(sl)}
    parti = [n for t, n in (("pec", "PEC"), ("email", "email"), ("telefono", "telefono"), ("orari", "orari")) if t in tipi]
    elenco = (", ".join(parti[:-1]) + " e " + parti[-1]) if len(parti) > 1 else (parti[0] if parti else "contatti")
    titolo = titolo_pagina(f"Cittadinanza Prefettura {di}: {elenco}",
                           f"Cittadinanza Prefettura {di}: PEC e contatti",
                           f"Cittadinanza Prefettura {di}: contatti",
                           f"Cittadinanza {nome}: contatti della Prefettura")
    descr = descrizione_pagina(loc["descrizione"])
    pagina(f"cittadinanza/{pref_url(sl)}/index.html", titolo, descr, corpo, jsonld)


def pagina_cittadinanza(prossime):
    """Indice /cittadinanza/: come si fa la domanda (dati nazionali con fonte) e le 106 prefetture per regione, con i contatti scritti
    da ognuna (solo caselle d'ufficio della Prefettura stessa) e il link alla pagina locale dove c'è qualcosa di locale da dire."""
    F, po = CITT["fonti"], CITT["polo_orienta"]
    letto = data_breve(max(f["verificato_il"] for f in F.values()))
    regioni = {}
    for sl, r in sorted(PREF.items(), key=lambda x: x[1]["nome"]):
        regioni.setdefault(r["regione"], []).append(sl)
    blocchi = []
    for reg in sorted(regioni):
        righe = []
        for sl in regioni[reg]:
            r = PREF[sl]
            nome = escape(r["nome"])
            cella_nome = (f'<a href="{pref_url(sl)}/"><strong>{nome}</strong></a>' if ha_pagina_pref(sl) else f"<strong>{nome}</strong>")
            if r["stato"] == 200:
                cc = contatti_di(sl)  # scelti a mano se ci sono, altrimenti i campi d'ufficio della pagina
                mail = "<br>".join(f'<a href="mailto:{escape(v)}">{escape(v)}</a>' for t, v, _ in cc if t in ("email", "pec")) or '<span class="small">non indicata</span>'
                quando = "<br>".join(escape(v) for t, v, _ in cc if t in ("orari", "ricevimento")) or '<span class="small">non indicato</span>'
                agg = data_it(r.get("ultimo_aggiornamento", ""))
                uff = f'<a href="{escape(r["url"])}" rel="noopener">pagina ufficiale</a>{f"<br><span class=small>aggiornata il {agg}</span>" if agg else ""}'
            else:
                mail, quando = '<span class="small">–</span>', '<span class="small">–</span>'
                uff = f'<a href="https://prefettura.interno.gov.it/it/prefetture" rel="noopener">elenco delle Prefetture</a><br><span class="small">pagina Cittadinanza non raggiungibile il {data_breve(r["letto_il"])}</span>'
            loc = f'<a href="{pref_url(sl)}/">Cosa scrive la Prefettura</a>' if ha_pagina_pref(sl) else '<span class="small">nulla di locale in più</span>'
            righe.append(f'<tr id="{pref_url(sl)}"><td>{cella_nome}</td><td data-l="Email e PEC">{mail}</td><td data-l="Ricevimento">{quando}</td>'
                         f'<td data-l="Fonte">{uff}</td><td data-l="Qui">{loc}</td></tr>')
        blocchi.append(f'<h3 id="{slug(reg)}">{escape(reg)}</h3><div class="tab-wrap rc-tab pref-tab"><table class="conf">'
                       '<thead><tr><th scope="col">Prefettura</th><th scope="col">Email e PEC dell\'ufficio</th><th scope="col">Ricevimento</th><th scope="col">Fonte</th><th scope="col">Qui</th></tr></thead>'
                       f'<tbody>{"".join(righe)}</tbody></table></div>')
    con_pagina = [sl for sl in PREF if ha_pagina_pref(sl)]
    lette = sum(1 for r in PREF.values() if r["stato"] == 200)
    griglia = "".join(f'<a href="{pref_url(sl)}/">{ic("edificio")}<span>{escape(PREF[sl]["nome"])}<small>Prefettura, cittadinanza</small></span></a>'
                      for sl in sorted(con_pagina, key=lambda x: PREF[x]["nome"]))
    faq = [
        ("Dove si presenta la domanda di cittadinanza italiana?",
         "Solo online, sul Portale Servizi del Ministero dell'Interno (ALI Cittadinanza), con SPID o CIE. La domanda poi la segue la Prefettura della provincia dove abiti."),
        ("Quanto costa la domanda di cittadinanza?",
         f"Il contributo è di {CITT['contributo_eur']} €: nella domanda si allega la ricevuta del pagamento. Servono anche gli estremi della marca da bollo telematica."),
        ("Quanto tempo ci vuole per la cittadinanza?",
         "Per le domande dal 20 dicembre 2020 la legge (art. 9-ter della legge 91/1992) fissa il termine in 24 mesi, prorogabili fino al massimo di 36 mesi dalla data della domanda, "
         "come scrive anche il Dipartimento per le libertà civili e l'immigrazione. È un termine di legge, non una previsione sulla tua pratica."),
        ("Come controllo lo stato della mia pratica di cittadinanza?",
         "Online, nel servizio del Ministero, con le stesse credenziali usate per la domanda. C'è anche il contact center Polo Orienta: "
         f"{po['telefono']}, {po['giorni']}, con il numero K10 della domanda."),
        ("Qual è la PEC per la cittadinanza?",
         f"Il Ministero indica {CITT['pec_ministero']}, con il numero della pratica (K10) nell'oggetto. Molte Prefetture indicano anche una loro PEC: la trovi nell'elenco qui sotto."),
        ("Serve l'esame B1 per la cittadinanza?",
         "Sì, per residenza e per matrimonio serve un certificato di italiano almeno B1, salvo alcuni esoneri (per esempio chi ha il permesso UE di lungo periodo o un titolo di studio italiano)."),
    ]
    faq_html = "".join(domanda(escape(q), escape(t)) for q, t in faq)
    jsonld = {"@context": "https://schema.org"} | faq_jsonld([(escape(q), escape(t)) for q, t in faq])
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Domanda di cittadinanza", None))}
<span class="occhiello">{ic("edificio")}Dopo l'esame B1 · fonti lette il {letto}</span>
<h1>Domanda di cittadinanza italiana, prefettura per prefettura</h1>
<p class="lead">La domanda di cittadinanza si manda solo online, sul Portale Servizi del Ministero dell'Interno con SPID o CIE, e costa {CITT["contributo_eur"]} € di contributo: lo scrive il Ministero dell'Interno (pagina letta il {letto}).
Qui sotto, per ognuna delle {len(PREF)} Prefetture, i contatti dell'ufficio cittadinanza scritti sulla sua pagina ufficiale.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{ic("web")}Dove</div><div class="r-data">Online <small>SPID o CIE</small></div><div class="r-cosa">Portale Servizi del Ministero dell'Interno</div></div>
<div class="slot"><div class="r-et">{ic("euro")}Quanto costa</div><div class="r-data">{CITT["contributo_eur"]} € <small>contributo</small></div><div class="r-cosa">più la marca da bollo telematica</div></div>
<div class="r-piede"><a href="#elenco">Trova la tua Prefettura {ic("freccia")}</a><span>{ic("doc")}Fonti: Ministero dell'Interno e Prefetture</span></div>
</div>
</section>
{avviso("Questo sito non è del Ministero né delle Prefetture e non dà consulenza sulla pratica. <strong>Decide la Prefettura.</strong> Per il tuo caso scrivi all'ufficio cittadinanza o chiedi a un patronato.")}
<section>
<h2 id="come">{ic("lista")}Come si presenta la domanda</h2>
{come_domanda("../")}
<p>Prima di inviarla controlla il <a href="../reddito-minimo-cittadinanza/">reddito minimo</a> (con il calcolatore) e il <a href="../#date">certificato B1</a>.</p>
</section>
<section>
<h2 id="dopo">{ic("orologio")}Dopo la domanda: tempi e stato della pratica</h2>
<ul>
<li><strong>Tempi:</strong> per le domande dal 20 dicembre 2020 la legge fissa il termine in <strong>24 mesi, prorogabili fino al massimo di 36</strong> dalla data di presentazione della domanda (<a href="{escape(F["legge"]["url"])}" rel="noopener">art. 9-ter della legge 91/1992</a>). È un termine di legge, non una previsione: la durata reale della tua pratica può essere diversa.</li>
<li><strong>Stato della pratica:</strong> si vede online, con le stesse credenziali usate per la domanda.</li>
<li><strong>Comunicazioni:</strong> il Ministero indica la PEC <a href="mailto:{CITT["pec_ministero"]}">{CITT["pec_ministero"]}</a>, una sola domanda per messaggio, con il numero K10 nell'oggetto; allegati in PDF, TIFF o JPEG fino a 5 MB l'uno e 15 MB in tutto.</li>
<li><strong>Polo Orienta</strong> (contact center del Ministero): tel. {po["telefono"]}, {po["giorni"]}, PEC <a href="mailto:{po["pec"]}">{po["pec"]}</a>. Tieni pronto il numero K10 e un documento.</li>
</ul>
{fonte_citt("legge", "residenza", "domanda", "consulta")}
</section>
{f'<section><h2 id="locali">{ic("edificio")}Prefetture con informazioni locali</h2><p>Per queste Prefetture abbiamo letto la pagina e riportato quello che scrivono di loro: contatti, orari, avvisi, regole sui documenti.</p><div class="griglia">{griglia}</div></section>' if griglia else ""}
<section>
<h2 id="elenco">{ic("pin")}Le {len(PREF)} Prefetture: contatti dell'ufficio cittadinanza</h2>
<p>Email e PEC sono quelle che ogni Prefettura scrive sulla sua pagina «Cittadinanza» ({lette} pagine lette il {data_breve(max(r["letto_il"] for r in PREF.values()))}); mostriamo solo le caselle d'ufficio della Prefettura stessa. «Non indicata»: la pagina non la scrive, usa il link alla pagina ufficiale.</p>
<div class="altre">{"".join(f'<a href="#{slug(r)}">{escape(r)}</a>' for r in sorted(regioni))}</div>
{"".join(blocchi)}
{fonte_citt("elenco")}
</section>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<div class="due">
<section>
<h2 id="esame">{ic("cal")}Non hai ancora il B1?</h2>
<p>Trovi <a href="../#date">tutte le date d'esame</a>, le <a href="../#citta">sedi per città</a>, <a href="../costo/">quanto costa</a> e <a href="../esonero-test-italiano/">chi è esonerato</a>.</p>
</section>
<aside>{modulo()}</aside>
</div>
{riquadro_preparati("../")}"""
    titolo = titolo_pagina("Domanda di cittadinanza: prefettura per prefettura, contatti",
                           "Domanda di cittadinanza: le 106 prefetture e i contatti")
    descr = descrizione_pagina(f"Domanda di cittadinanza italiana: online con SPID, contributo di {CITT['contributo_eur']} €, termine di legge 24-36 mesi. "
                               "Email e PEC dell'ufficio cittadinanza di ogni Prefettura.",
                               f"Domanda di cittadinanza: online con SPID, contributo di {CITT['contributo_eur']} €, termine di legge 24-36 mesi. "
                               "Email e PEC dell'ufficio cittadinanza di ogni Prefettura.")
    pagina("cittadinanza/index.html", titolo, descr, corpo, jsonld)


def privacy():
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("it", SITO_ID, ci_sono_affiliati()) or """<h2>Cookie e contatore visite</h2><p>Questo sito non usa cookie di profilazione. Per contare le visite usiamo <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, un contatore rispettoso della privacy: non usa cookie e non salva nulla nel browser, non crea profili e non conserva l'indirizzo IP, la firma completa del browser né altri identificativi. Tiene solo numeri aggregati (pagina, ora o giorno, browser, Paese, larghezza dello schermo) su server nell'Unione europea e non cede nulla a terzi; vedi l'<a href="https://www.goatcounter.com/help/privacy" rel="noopener">informativa privacy di GoatCounter</a>.</p>"""
    corpo = f"""<section class="hero">{briciole(("EsameB1", "./"), ("Privacy", None))}<h1>Informativa privacy</h1><p class="small">Ultimo aggiornamento: ottobre 2026</p></section>
<h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce {NOME} come progetto indipendente. Puoi scriverci rispondendo a qualsiasi email che ti mandiamo.</p>
<h2>Quali dati raccogliamo</h2><p>Solo se compili il modulo "Avvisami": la tua email, la città e l'ente che scegli, e la pagina o il link da cui arrivi (per capire quali canali funzionano).</p>
<h2>Perché</h2><p>Per mandarti avvisi sulle date e sulle scadenze dell'esame B1. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi ritirare quando vuoi.</p>
<h2>Chi li gestisce per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i dati del modulo per nostro conto. Netlify può trattare i dati fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>
{cookie}{PRIVACY_AMAZON if url_affiliato("amazon") else ""}
<h2>Per quanto tempo</h2><p>Finché resti iscritto agli avvisi. Se chiedi la cancellazione, cancelliamo i tuoi dati.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e puoi fare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>"""
    pagina("privacy.html", "Privacy | EsameB1", "Informativa privacy del sito EsameB1.", corpo)


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
  # Pubblica solo se è cambiato qualcosa in esameb1/sito (ogni pubblicazione consuma crediti Netlify).
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

# La pagina delle prove d'esempio è diventata la sezione /esempi/ (31/10/2026): il vecchio indirizzo resta valido.
[[redirects]]
  from = "/esempi-esame-b1"
  to = "/esempi/"
  status = 301
  force = true

[[redirects]]
  from = "/esempi-esame-b1/*"
  to = "/esempi/"
  status = 301
  force = true

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
        if not sedi_di(c):
            errori.append(f"città senza sedi: {c['nome']}")
    if not prossime:
        errori.append("nessuna sessione futura")
    # sezione /cittadinanza/ e redditi (31/10/2026): ogni punto e contatto locale con la frase della fonte; fonti con data
    for sl, p in PREF_LOC["prefetture"].items():
        if sl not in PREF:
            errori.append(f"prefetture_locali.json: prefettura sconosciuta {sl}")
        for x in p.get("punti", []) + p.get("contatti", []):
            if not x.get("citazioni"):
                errori.append(f"prefetture_locali.json: {sl}: voce senza citazione: {x.get('titolo') or x.get('valore')}")
        for x in p.get("contatti", []):
            if x["tipo"] not in TIPI_CONTATTO:
                errori.append(f"prefetture_locali.json: {sl}: tipo di contatto sconosciuto {x['tipo']}")
    for f in list(CITT["fonti"].values()) + list(REDDITI["cittadinanza"]["fonti"].values()) + list(REDDITI["carta_soggiorno"]["fonti"].values()):
        if not f.get("url") or not f.get("verificato_il"):
            errori.append(f"fonte senza url o data: {f.get('nome')}")
    c = REDDITI["cittadinanza"]
    for caso in c["casi_pdf"]:  # la tabella del PDF della Prefettura deve coincidere con la formula
        if calcola_redditi(caso["coniuge"], caso["figli"], 0)["cittadinanza"]["soglia"] != cent(caso["importo"]):
            errori.append(f"redditi.json: caso {caso} diverso dalla formula")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    prossime = sorted(future(sessioni), key=lambda s: (s["data"], s["ente"]))
    controlli(prossime)
    controlli_ricongiungimento()
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
    for e in enti:
        pagina_risultati_ente(e, prossime)
        urls.append(f"risultati/{SLUG_RISULTATI[e['sigla']]}/")
    pagina_esenzioni()
    urls.append("esenzioni-e-domande/")
    pagina_esempi(prossime)
    urls.append("esempi/")
    for e in esempi["enti"]:
        pagina_esempi_ente(e, prossime)
        urls.append(f"esempi/{SLUG_ENTE[e['sigla']]}/")
    pagina_confronto(prossime)
    urls.append("esempi/confronto/")
    pagina_esonero()
    urls.append("esonero-test-italiano/")
    pagina_ricongiungimento()
    urls.append("reddito-ricongiungimento-familiare/")
    pagina_redditi()
    urls.append("reddito-minimo-cittadinanza/")
    pagina_cittadinanza(prossime)
    urls.append("cittadinanza/")
    for sl in sorted(PREF):
        if ha_pagina_pref(sl):
            pagina_prefettura(sl, prossime)
            urls.append(f"cittadinanza/{pref_url(sl)}/")
    privacy()
    urls.append("privacy.html")
    urls += EN.genera(sys.modules[__name__], prossime)  # sezione inglese /en/ (genera_en.py)
    urls += LG.genera(sys.modules[__name__], prossime)  # sezioni /uk/ e /ro/ (genera_lingue.py, pagine in genera_lingue_pagine.py)
    extra(urls)
    n_en = EN.controlli(sys.modules[__name__])  # cifre /en/ = cifre italiane, link tra le lingue
    n_l = LG.controlli(sys.modules[__name__])  # cifre /uk/ e /ro/, hreflang reciproci su tutto il sito, calcolatore identico in 4 lingue
    print(f"Sito generato in {SITO}: {len(urls)} pagine ({n_en} in inglese, {n_l['uk']} in ucraino, {n_l['ro']} in rumeno, controllate), "
          f"{len(prossime)} sessioni future, {len(sedi)} sedi.")


if __name__ == "__main__":
    main()
