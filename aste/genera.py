"""Genera il sito statico "Aste in Chiaro" (italiano) in aste/sito/ da aste/dati/.

Uso (dalla radice del repository):
    python3 aste/raccolta/aggiorna.py   # ogni giorno: dati PVP e OMI in aste/dati/ (anche live.json)
    python3 aste/genera.py              # ogni settimana: pagine in aste/sito/
    python3 aste/verifica.py --browser  # controlli prima di pubblicare

Dati:
    dati/lotti.json     case all'asta dei comuni con una pagina (solo campi del lotto, niente dati personali)
    dati/auto.json      veicoli all'asta (pagina nazionale)
    dati/omi.json       quotazioni OMI delle zone che contengono almeno un lotto («Agenzia delle Entrate – OMI», CC BY 4.0)
    dati/live.json      prezzi e date aggiornati ogni giorno: le pagine lo leggono da GitHub (URL_LIVE) e nascondono le aste passate
    dati/affiliati.json riquadro "mutuo": nascosto finché non c'è un URL (mai inventarlo)
"""
import hashlib
import json
import re
import shutil
import sys
import statistics
import unicodedata
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://aste-giudiziarie-sconti.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
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
SITO_ID = "aste"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_"))


def riquadro_trasparenza(corpo, lingua="it"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Alcuni link sono di affiliazione: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


URL_LIVE = "https://raw.githubusercontent.com/massimilianocori/copertine-libri/ccr-b7fd6b9e-n096cr/aste/dati/live.json"
NOME = "Aste in Chiaro"
PVP = "https://pvp.giustizia.it/pvp/"
PVP_LOTTO = "https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio={}"
PVP_GUIDA = "https://pvp.giustizia.it/pvp/it/guida.page"
MG_VENDITE = "https://www.giustizia.it/giustizia/page/it/vendite_giudiziarie"
OMI_FORNITURE = "https://www.agenziaentrate.gov.it/portale/schede/fabbricatiterreni/omi/forniture-dati-omi"
OMI_GEOPOI = "https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm"
OMI_MANUALI = "https://www.agenziaentrate.gov.it/portale/web/guest/schede/fabbricatiterreni/omi/manuali-e-guide"
CC_BY = "https://creativecommons.org/licenses/by/4.0/deed.it"
NORMATTIVA_CPC = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443~art{}"
NORMATTIVA_CC = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262~art{}"
NORMATTIVA_DISPATT_CC = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-30;318~art63"
NORMATTIVA_DM32 = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:ministero.giustizia:decreto:2015-02-26;32"
CONTROLLO_NORME = "2026-10-15"  # data in cui abbiamo riletto su Normattiva gli articoli citati nelle guide
SOGLIA_CITTA = 8   # lotti per una pagina città
SOGLIA_FASCIA = 5  # lotti per una pagina fascia di prezzo
SOGLIA_ZONA = 4    # lotti per una pagina zona OMI
SOGLIA_CITTA_FASCE = 15  # lotti della città perché abbia pagine per fascia di prezzo
QUOTA_MAX = 0.7    # una fascia o una zona con più del 70% delle aste della città non ha pagina (doppione)
ROMA = ZoneInfo("Europe/Rome")
ADESSO = datetime.now(ROMA)
OGGI = ADESSO.date()


def carica(nome, default=None):
    try:
        return json.loads((DATI / nome).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        if default is not None:
            return default
        raise


LOTTI_J = carica("lotti.json")
AUTO_J = carica("auto.json", {"veicoli": []})
OMI = carica("omi.json")
AFFILIATI = carica("affiliati.json", {})
LETTO = LOTTI_J["letto_il"]
SEM = OMI["semestre"]
SEM_TESTO = f"{SEM[4]}° semestre {SEM[:4]}"
SEM_BREVE = f"{SEM[4]}° sem. {SEM[:4]}"
ATTRIB = "Agenzia delle Entrate – OMI"

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
MES = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
GG = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]
DISP = {
    "libero": ("Libero", "b-lib", "Libero secondo l'annuncio"),
    "occupato": ("Occupato", "b-occ", "Occupato secondo l'annuncio"),
    "senza_titolo": ("Occupato senza titolo", "b-occ", "Occupato da chi non ha un titolo valido contro la procedura"),
    "liberazione": ("In liberazione", "b-neu", "Liberazione in corso secondo l'annuncio"),
    "misto": ("Occupazione mista", "b-neu", "Più beni con stati diversi: vedi la scheda"),
    "nd": ("Occupazione non indicata", "b-nd", "Il PVP non indica se è libero o occupato"),
}
FASCE = [
    ("fino-a-50000-euro", "fino a 50.000 €", 0, 50000),
    ("da-50000-a-100000-euro", "da 50.000 a 100.000 €", 50001, 100000),
    ("da-100000-a-200000-euro", "da 100.000 a 200.000 €", 100001, 200000),
    ("oltre-200000-euro", "oltre 200.000 €", 200001, 10 ** 12),
]
RISERVATI = {"assets", "citta", "guide", "metodologia", "chi-siamo", "contatti", "auto-all-asta", "data", "privacy"}


# ---------------------------------------------------------------- formati
def h(x):
    return escape(str(x))


def intero(x):
    return f"{round(x):,}".replace(",", ".")


def euro(x):
    return "–" if x is None else f"{intero(x)} €"


def euro_breve(x):
    if x >= 1_000_000:
        return f"{x / 1_000_000:.1f}".replace(".", ",").replace(",0", "") + " mln €"
    return euro(x)


def dt(iso):
    return datetime.fromisoformat(iso[:16])


def data_lunga(iso):
    d = date.fromisoformat(iso[:10])
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def data_asta(iso):
    d = dt(iso)
    s = f"{GIORNI[d.weekday()]} {d.day} {MESI[d.month - 1]} {d.year}"
    return s + (f", ore {d:%H:%M}" if len(iso) > 10 else "")


def data_breve(iso):
    d = date.fromisoformat(iso[:10])
    return f"{d.day} {MES[d.month - 1]} {d.year}"


def letto_testo(iso):
    d = datetime.fromisoformat(iso)
    return f"{d.day} {MESI[d.month - 1]} {d.year} alle {d:%H:%M}"


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", norm(t)).strip("-")


def plur(n, uno, molti):
    return f"{intero(n)} {uno if n == 1 else molti}"


def sconto_testo(s):
    if s is None:
        return ""
    if s <= -3:
        return "sotto la media OMI di zona"
    if s >= 3:
        return "sopra la media OMI di zona"
    return "in linea con la media OMI di zona"


def sconto_cls(s):
    return "down" if s is not None and s <= -3 else ("up" if s is not None and s >= 3 else "neu")


def mediana(v):
    return statistics.median(v) if v else None


# ---------------------------------------------------------------- dati: città, zone, fasce
LOTTI = [L for L in LOTTI_J["lotti"] if L["data"] >= ADESSO.strftime("%Y-%m-%dT%H:%M")]
SCADUTI_ALLA_GENERAZIONE = len(LOTTI_J["lotti"]) - len(LOTTI)
CITTA = {}
for L in LOTTI:
    CITTA.setdefault((L["comune"], L["prov"]), []).append(L)
CITTA = {k: v for k, v in CITTA.items() if len(v) >= SOGLIA_CITTA}
_nomi = {}
for (c, p) in CITTA:
    _nomi.setdefault(slug(c), []).append(p)
SLUG_CITTA = {}
for (c, p) in CITTA:
    s = slug(c)
    if len(_nomi[s]) > 1 or s in RISERVATI:
        s = f"{s}-{p.lower()}"
    SLUG_CITTA[(c, p)] = s
LOTTI = [L for L in LOTTI if (L["comune"], L["prov"]) in CITTA]
NUOVO_DAL = (OGGI - timedelta(days=7)).isoformat()
RECENTI_DAL = (OGGI - timedelta(days=21)).isoformat()


MINUSCOLE = {"di", "del", "della", "dei", "delle", "degli", "dello", "da", "dal", "dalla", "e", "ed", "in", "a", "al", "alla", "ai",
             "agli", "alle", "sul", "sulla", "per", "con", "tra", "fra", "lo", "la", "le", "il", "i", "gli"}


def pulisci_zona(n):
    """'QUART.MURAT -TRA C.SO VITT.VENETO,CASTELLO SVEVO' -> 'Quart. Murat - tra C.so Vitt. Veneto, Castello Svevo'."""
    s = str(n or "").replace("’", "'").replace("`", "'").lower()
    # accenti scritti come apostrofo nel GEOPOI («PIETA`», «LOCALITA'») o mancanti («LIBERTA»)
    s = re.sub(r"([aeiou])'(?=[^a-z]|$)", lambda m: {"a": "à", "e": "è", "i": "ì", "o": "ò", "u": "ù"}[m.group(1)], s)
    s = re.sub(r"\b(liberta|citta|localita|universita|trinita|pieta|sanita|carita|unita|attivita)\b(?!')",
               lambda m: m.group(1)[:-1] + "à", s)
    s = re.sub(r"(?<=[a-z]{3})\.(?=[a-z])", ". ", s)
    s = re.sub(r"(?<![a-z])([a-z])\.(?=[a-z]{4,})", r"\1. ", s)
    s = re.sub(r"^confini\s*:\s*", "", s)
    s = re.sub(r"\s*\b(?:tu|aab|fv|ts|ad|ap)\.\s?[amb]\b\.?", "", s)  # sigle interne di Genova («MARASSI TU.M», «BAVARI AAB.M»)
    s = re.sub(r",(?=\S)", ", ", s)
    s = re.sub(r"\s*-+\s*", " – ", s)
    s = re.sub(r"\s+", " ", s).strip()
    out = []
    for i, w in enumerate(s.split(" ")):
        if i and w in MINUSCOLE:
            out.append(w)
        else:
            out.append(re.sub(r"^([^a-zà-ù]*)([a-zà-ù])", lambda m: m.group(1) + m.group(2).upper(), w))
    s = " ".join(out)
    s = re.sub(r"'([a-zà-ù])", lambda m: "’" + m.group(1).upper(), s)
    return re.sub(r"(?<=\s)(D|Dell|Dall|Nell|Sull|All|L)’", lambda m: m.group(1).lower() + "’", s)  # «Medaglie d’Oro»


def nome_zona(cod, z, breve=True):
    Z = OMI["comuni"].get(cod, {}).get("zone", {}).get(z)
    if not Z:
        return z
    n = pulisci_zona(Z["nome"])
    if not breve:
        return n
    n = re.sub(r"\s*\(.*?\)\s*", " ", n).strip() or n
    if len(n) > 42:
        # quante più parti intere stanno in 42 caratteri: «Monza, Crescenzago, Gorla» e non solo «Monza»
        parti, corto = re.split(r"(,\s*| – | / )", n), ""
        for i in range(0, len(parti), 2):
            prova = corto + (parti[i - 1] if i else "") + parti[i]
            if len(prova.strip()) > 42:
                break
            corto = prova
        n = corto.strip(" ,–/") or n
    if len(n) > 42:
        n = n[:42].rsplit(" ", 1)[0].rstrip(" ,-") + "…"
    return n


def url_citta(k):
    return SLUG_CITTA[k] + "/"


def url_zona(k, cod, z):
    return f"{SLUG_CITTA[k]}/zona-{z.lower()}-{slug(nome_zona(cod, z))}/"


def zone_citta(k):
    """Zone OMI con almeno SOGLIA_ZONA lotti nella città."""
    zz = {}
    for L in CITTA[k]:
        if L.get("zona"):
            zz.setdefault(tuple(L["zona"]), []).append(L)
    # niente pagina se la zona contiene quasi tutte le aste della città (sarebbe un doppione della pagina città)
    return {z: v for z, v in zz.items() if len(v) >= SOGLIA_ZONA and len(v) <= QUOTA_MAX * len(CITTA[k])}


def fasce_citta(k):
    out = []
    for f in FASCE:
        v = [L for L in CITTA[k] if f[2] <= L["base"] <= f[3]]
        if len(v) >= SOGLIA_FASCIA and len(CITTA[k]) >= SOGLIA_CITTA_FASCE and len(v) <= QUOTA_MAX * len(CITTA[k]):
            out.append((f, v))
    return out


def ordina_sconto(lotti):
    con = sorted([L for L in lotti if L.get("sconto_min") is not None], key=lambda L: (L["sconto_min"], L["data"]))
    senza = sorted([L for L in lotti if L.get("sconto_min") is None], key=lambda L: (L["data"], L["id"]))
    return con + senza


# ---------------------------------------------------------------- stile e script (file esterni con impronta nel nome)
CSS = """
@font-face{font-family:"Source Serif 4";src:url(/assets/fonts/source-serif-4.woff2) format("woff2");font-weight:200 900;font-style:normal;font-display:swap}
@font-face{font-family:"Figtree";src:url(/assets/fonts/figtree.woff2) format("woff2");font-weight:300 900;font-style:normal;font-display:swap}
:root{--bg:#F7F4EF;--card:#FFFFFF;--ink:#1E1C19;--ink-2:#47423B;--ink-3:#6B645A;--line:#E6DFD4;--line-2:#D3C9BA;
--deep:#1C2E2A;--deep-2:#27413B;--on-deep:#F4F0E9;--on-deep-2:#B8C7C0;--accent:#A5412A;--accent-h:#82311E;--accent-2:#F8E9E2;--on-accent:#FFFFFF;
--gold:#D9A23A;--gold-ink:#7E5600;--gold-2:#FBF1DC;--down:#17744A;--down-2:#E2F3EA;--up:#A8402A;--up-2:#FAE7E1;--neu-2:#EEF0EF;
--mute:#F2EDE5;--track:#ECE5DA;--omi:#C9DDD4;--omi-ink:#1C2E2A;
--sh-1:0 1px 2px rgba(28,46,42,.06),0 1px 1px rgba(28,46,42,.04);--sh-2:0 20px 40px -24px rgba(28,46,42,.38),0 2px 8px rgba(28,46,42,.06);
--r:14px;--r-s:10px;--serif:"Source Serif 4",Charter,"Iowan Old Style",Georgia,serif;--sans:Figtree,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11100E;--card:#1B1916;--ink:#F2EDE6;--ink-2:#D2CABF;--ink-3:#A79F94;--line:#2F2B26;--line-2:#3F3A33;
--deep:#0C1513;--deep-2:#15251F;--on-deep:#EEE9E1;--on-deep-2:#A9B8B1;--accent:#F0916E;--accent-h:#F6AF95;--accent-2:#3A2219;--on-accent:#1A0D08;
--gold:#E8B95A;--gold-ink:#E8B95A;--gold-2:#2D2412;--down:#72D6A4;--down-2:#142A20;--up:#FFA48D;--up-2:#351C15;--neu-2:#24282A;
--mute:#221F1B;--track:#2D2924;--omi:#2B4840;--omi-ink:#E6F2EC;--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 20px 40px -22px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#11100E;--card:#1B1916;--ink:#F2EDE6;--ink-2:#D2CABF;--ink-3:#A79F94;--line:#2F2B26;--line-2:#3F3A33;
--deep:#0C1513;--deep-2:#15251F;--on-deep:#EEE9E1;--on-deep-2:#A9B8B1;--accent:#F0916E;--accent-h:#F6AF95;--accent-2:#3A2219;--on-accent:#1A0D08;
--gold:#E8B95A;--gold-ink:#E8B95A;--gold-2:#2D2412;--down:#72D6A4;--down-2:#142A20;--up:#FFA48D;--up-2:#351C15;--neu-2:#24282A;
--mute:#221F1B;--track:#2D2924;--omi:#2B4840;--omi-ink:#E6F2EC;--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 20px 40px -22px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--gold);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20}
header.top .wrap{display:flex;align-items:center;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.22rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;letter-spacing:-.01em;margin-right:auto}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:var(--gold);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.08)}
.tema{display:grid;place-items:center;width:42px;height:42px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--gold)}.tema .ico{width:20px;height:20px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:.95rem;padding:9px 13px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep);min-height:42px}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--gold)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{padding:12px 14px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600}.nav-m nav a:hover{background:var(--accent-2)}
.band{background:var(--deep);color:var(--on-deep);position:relative;overflow:hidden}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(800px 320px at 88% -20%,rgba(217,162,58,.20),transparent 60%),radial-gradient(700px 300px at -10% 120%,rgba(165,65,42,.25),transparent 60%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band-in{position:relative;z-index:1;padding:30px 16px 72px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin:0 0 12px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.012em}
h1{font-size:clamp(1.8rem,5vw,2.8rem);line-height:1.12;margin:0 0 12px;text-wrap:balance;max-width:860px}
.band h1{color:#fff}
.sub{font-size:1.07rem;color:var(--on-deep-2);margin:0 0 16px;max-width:720px}.sub strong{color:var(--on-deep)}
.trust{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--on-deep-2);margin:0;padding:0;list-style:none}
.trust li{display:inline-flex;align-items:center;gap:7px}.trust .ico{color:var(--gold)}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.35rem,3vw,1.62rem);line-height:1.2;margin:44px 0 12px;text-wrap:balance}
h3{font-size:1.12rem;margin:24px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:780px;margin:0 0 12px}
.small{font-size:.87rem;color:var(--ink-3)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-52px;position:relative;z-index:2}
.stat-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);overflow:hidden}
.stat{padding:16px 18px;min-width:0;border-right:1px solid var(--line)}.stat:last-child{border-right:0}
.stat b{display:block;font-family:var(--serif);font-size:clamp(1.35rem,3.4vw,1.75rem);line-height:1.1;font-variant-numeric:tabular-nums;color:var(--ink)}
.stat span{display:block;font-size:.83rem;color:var(--ink-3);margin-top:5px;line-height:1.35}
.stat b.down{color:var(--down)}
.agg{display:flex;align-items:flex-start;gap:8px;font-size:.86rem;color:var(--ink-3);margin:12px 2px 0}
.agg .ico{color:var(--down);margin-top:.25em}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.chips a{display:inline-flex;align-items:center;gap:6px;padding:8px 13px;border-radius:999px;border:1px solid var(--line-2);background:var(--card);color:var(--ink);text-decoration:none;font-weight:600;font-size:.92rem;white-space:nowrap}
.chips a small{color:var(--ink-3);font-weight:500;font-variant-numeric:tabular-nums}
.chips a:hover{border-color:var(--accent);color:var(--accent)}
.strumenti{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;margin:22px 0 14px}
.filtri{display:inline-flex;flex-wrap:wrap;gap:6px}
.filtri button{font:inherit;font-size:.9rem;font-weight:600;padding:8px 13px;border-radius:999px;border:1px solid var(--line-2);background:var(--card);color:var(--ink-2);cursor:pointer;min-height:40px}
.filtri button[aria-pressed="true"]{background:var(--deep);border-color:var(--deep);color:var(--on-deep)}
:root[data-theme="dark"] .filtri button[aria-pressed="true"]{background:var(--on-deep);color:var(--deep);border-color:var(--on-deep)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .filtri button[aria-pressed="true"]{background:var(--on-deep);color:var(--deep);border-color:var(--on-deep)}}
.ordina{display:inline-flex;align-items:center;gap:8px;font-size:.9rem;color:var(--ink-3)}
.ordina select{font:inherit;font-size:.92rem;color:var(--ink);background:var(--card);border:1px solid var(--line-2);border-radius:10px;padding:8px 10px;min-height:40px}
.conta{font-size:.92rem;color:var(--ink-2);margin:0 0 10px}.conta b{font-variant-numeric:tabular-nums}
.lotti{display:grid;gap:14px;margin:0;padding:0;list-style:none}
.lotto{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-1);padding:18px 20px;display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);grid-template-areas:"testa testa" "tit tit" "sx omi" "link omi";gap:8px 26px;min-width:0}
.l-testa{grid-area:testa;display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}
.l-tipo{font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin-right:4px}
.badge{display:inline-flex;align-items:center;gap:5px;font-size:.8rem;font-weight:700;padding:3px 9px;border-radius:999px;white-space:nowrap;line-height:1.35}
.b-lib{background:var(--down-2);color:var(--down)}.b-occ{background:var(--up-2);color:var(--up)}.b-neu{background:var(--gold-2);color:var(--gold-ink)}.b-nd{background:var(--neu-2);color:var(--ink-2)}
.b-new{background:var(--accent);color:var(--on-accent)}.b-quota{background:var(--gold-2);color:var(--gold-ink)}
.l-tit{grid-area:tit;font-family:var(--serif);font-size:1.2rem;line-height:1.3;margin:2px 0 0}
.l-tit small{display:block;font-family:var(--sans);font-size:.88rem;font-weight:500;color:var(--ink-3);margin-top:2px}
.l-tit small a{color:inherit}
.l-sx{grid-area:sx;min-width:0}.omi{grid-area:omi}.l-link{grid-area:link;align-self:end}
.prezzi{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0 12px}
.prezzi div{background:var(--mute);border-radius:var(--r-s);padding:10px 12px;min-width:0}
.prezzi span{display:block;font-size:.76rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}
.prezzi b{display:block;font-family:var(--serif);font-size:1.32rem;line-height:1.2;font-variant-numeric:tabular-nums;white-space:nowrap}
.prezzi .pm{background:var(--accent-2)}.prezzi .pm b{color:var(--accent)}
.info{list-style:none;margin:0;padding:0;display:grid;gap:5px;font-size:.92rem;color:var(--ink-2)}
.info li{display:flex;gap:8px;align-items:flex-start}.info .ico{color:var(--ink-3);margin-top:.22em}
.omi{border-left:1px solid var(--line);padding-left:22px;display:flex;flex-direction:column;gap:6px;min-width:0}
.sc{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 8px;margin:6px 0 0}
.sc b{font-family:var(--serif);font-size:1.9rem;line-height:1;font-variant-numeric:tabular-nums}
.sc span{font-weight:700;font-size:.95rem}
.sc.down b,.sc.down span{color:var(--down)}.sc.up b,.sc.up span{color:var(--up)}.sc.neu b,.sc.neu span{color:var(--ink-2)}
.omi p{margin:0}.omi .det{font-size:.88rem;color:var(--ink-2);line-height:1.5}
.scala{position:relative;height:30px;margin:10px 0 2px}
.scala .t{position:absolute;left:0;right:0;top:12px;height:6px;border-radius:999px;background:var(--track)}
.scala .r{position:absolute;top:8px;height:14px;border-radius:4px;background:var(--omi)}
.scala .m{position:absolute;top:2px;width:3px;height:26px;border-radius:2px;transform:translateX(-1.5px)}
.scala .m.min{background:var(--accent)}.scala .m.base{background:var(--ink-3)}
.leg{display:flex;flex-wrap:wrap;gap:3px 12px;font-size:.78rem;color:var(--ink-3);margin:0}
.leg i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.leg .k1{background:var(--accent)}.leg .k2{background:var(--ink-3)}.leg .k3{background:var(--omi)}
.nocalc{font-size:.9rem;color:var(--ink-2);background:var(--mute);border-radius:var(--r-s);padding:10px 12px;margin-top:6px}
.nocalc b{display:block;color:var(--ink);font-size:.93rem}
.pvp{display:inline-flex;align-items:center;gap:7px;font-weight:700;font-size:.95rem;margin-top:4px;text-decoration:none}
.pvp:hover{text-decoration:underline}
.vuoto{background:var(--card);border:1px dashed var(--line-2);border-radius:var(--r);padding:22px;text-align:center;color:var(--ink-2)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;flex-direction:column;gap:2px;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:700;min-width:0;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px)}
.griglia a small{font-weight:500;color:var(--ink-3);font-size:.86rem;font-variant-numeric:tabular-nums}
.cittablocco{margin:34px 0 0}
.cittablocco .tit{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 16px;margin:0 0 12px}
.cittablocco h3{font-size:1.3rem;margin:0}.cittablocco .tit a{font-weight:700;font-size:.95rem;white-space:nowrap}
.passi{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:0;padding:0;list-style:none;counter-reset:p}
.passi li{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px;box-shadow:var(--sh-1);counter-increment:p}
.passi li::before{content:counter(p);display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--accent-2);color:var(--accent);font-weight:800;margin-bottom:8px}
.passi b{display:block;font-family:var(--serif);font-size:1.08rem;margin-bottom:4px}.passi p{margin:0;font-size:.94rem;color:var(--ink-2)}
.guide{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin:0;padding:0;list-style:none}
.guide a{display:block;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;text-decoration:none;color:var(--ink);box-shadow:var(--sh-1)}
.guide a:hover{border-color:var(--accent)}.guide b{display:block;font-family:var(--serif);font-size:1.08rem;margin-bottom:4px;color:var(--ink)}.guide span{font-size:.92rem;color:var(--ink-2)}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1)}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
td.n,th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
th{background:var(--mute);font-size:.74rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
tbody tr:last-child td{border-bottom:0}
@media (max-width:640px){.ct thead{display:none}.ct,.ct tbody,.ct tr,.ct td{display:block}
.ct tr{display:flex;flex-wrap:wrap;gap:2px 14px;padding:12px 14px;border-bottom:1px solid var(--line)}.ct tbody tr:last-child{border-bottom:0}
.ct td{border:0;padding:0;text-align:left!important}.ct td:first-child{flex:1 1 100%;font-weight:700}
.ct td[data-l]::before{content:attr(data-l) " ";color:var(--ink-3);font-size:.8rem}}
.nota{position:relative;background:var(--gold-2);border:1px solid color-mix(in srgb,var(--gold) 45%,transparent);padding:12px 16px 12px 46px;border-radius:var(--r-s);font-size:.93rem;margin:18px 0;color:var(--ink)}
.nota .ico{position:absolute;left:16px;top:14px;color:var(--gold-ink);width:20px;height:20px}
.fonti-box{margin-top:44px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--deep-2);border-radius:var(--r-s);padding:16px 20px;font-size:.9rem;color:var(--ink-2)}
.fonti-box h2{display:flex;align-items:center;gap:8px;font-size:1.1rem;margin:0 0 8px;color:var(--ink)}
.fonti-box ul{margin:0 0 8px;padding-left:18px}.fonti-box li{margin-bottom:6px}.fonti-box p{margin:6px 0}.fonti-box a{overflow-wrap:anywhere}
.mutuo-box{margin:26px 0;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--accent-2);border:1px solid color-mix(in srgb,var(--accent) 30%,transparent);border-radius:var(--r);padding:18px 20px}
.mutuo-box p{margin:0;max-width:640px}.mutuo-box .small{margin-top:4px}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-weight:700;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:12px 20px;cursor:pointer;min-height:46px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}.btn:disabled{opacity:.6;cursor:wait}
.ad-slot{margin:24px 0}.ad-slot:empty{display:none}
.testo{max-width:780px}.testo p,.testo li{max-width:780px}.testo h2{margin-top:36px}.testo li{margin-bottom:6px}
.testo .indice{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:14px 18px 10px;margin:8px 0 10px}
.testo .indice b{display:block;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px}
.testo .indice ol{margin:0;padding-left:20px}
.avviso{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:14px 18px;margin:20px 0;font-size:.95rem}
.avviso b{color:var(--ink)}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
.form{display:grid;gap:14px}.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}.form .check input{width:auto;min-height:0;margin-top:4px}
.hp{position:absolute;left:-9999px}.ok{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:var(--r-s)}.errore{color:var(--up);font-weight:600}
footer{margin-top:64px;background:var(--deep);color:var(--on-deep-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--on-deep)}footer a:hover{color:var(--gold)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}footer p{margin:0 0 10px;max-width:680px}footer strong{color:var(--on-deep)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
@media (max-width:900px){.lotto{grid-template-columns:1fr;grid-template-areas:"testa" "tit" "sx" "omi" "link"}.l-link{border-top:1px solid var(--line);padding-top:10px;margin-top:4px}.omi{border-left:0;padding-left:0;border-top:1px solid var(--line);padding-top:12px}.passi{grid-template-columns:1fr}.cols{grid-template-columns:1fr}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:22px}
.stat-row{grid-template-columns:repeat(2,minmax(0,1fr))}.stat:nth-child(2){border-right:0}.stat:nth-child(-n+2){border-bottom:1px solid var(--line)}}
@media (max-width:480px){.lotto{padding:16px}.prezzi b{font-size:1.18rem}.prezzi div{padding:9px 10px}.stat{padding:13px 14px}.strumenti{align-items:stretch}.ordina{width:100%}.ordina select{flex:1}}
@media (max-width:360px){.prezzi{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""
CSS = re.sub(r"\n", "", CSS)

ICONE = {
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "doc": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8 13h8M8 17h5"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "house": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5h4v5"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3.5 2"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "ext": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 19V7.5A1.5 1.5 0 0 1 5.5 6H10"/>',
    "pin": '<path d="M12 21.5s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "gavel": '<path d="m14.5 3.5 6 6M12 6l6 6M9.5 8.5l6 6M13 10.5l-9 9"/><path d="M3 21h8"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="m8 12.5 2.8 2.8L16.5 9.5"/>',
    "car": '<path d="M5 16.5h14M6.5 16.5V19M17.5 16.5V19M4 16.5v-4l2-5.5h12l2 5.5v4"/><circle cx="7.5" cy="13.5" r="1"/><circle cx="16.5" cy="13.5" r="1"/>',
    "tag": '<path d="M3 12V4.5A1.5 1.5 0 0 1 4.5 3H12l9 9-9 9z"/><circle cx="8" cy="8" r="1.5"/>',
    "scale": '<path d="M12 3v18M5 7h14M7 7l-3 7a3 3 0 0 0 6 0zM17 7l-3 7a3 3 0 0 0 6 0z"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
}
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>\n")
ICONS_FILE = f"icons.{hashlib.sha256(SPRITE.encode()).hexdigest()[:10]}.svg"


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# Marchio: casa con tetto e una freccia in giù dorata (prezzo sotto la media), su tessera verde scuro
_M = ('<rect width="40" height="40" rx="10" fill="#1C2E2A"/>'
      '<path d="M8.5 19.5 20 10l11.5 9.5" fill="none" stroke="#F4F0E9" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
      '<path d="M12 17v13h16V17" fill="none" stroke="#F4F0E9" stroke-width="2.6" stroke-linejoin="round"/>'
      '<path d="M20 18.5v8M16.6 23.4 20 26.8l3.4-3.4" fill="none" stroke="#D9A23A" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{_M}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('aste-tema');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"
APP_JS = r"""
(function(){
  var R=document.documentElement;
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var c=R.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';R.setAttribute('data-theme',n);try{localStorage.setItem('aste-tema',n);}catch(e){}});
  var src=document.querySelectorAll('input[name=source]');var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'diretto';}catch(e){ref='diretto';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});

  // ---- aste: numeri in formato italiano, ora di Roma, aggiornamento da live.json
  function num(x){return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g,'.');}
  function eur(x){return num(x)+' €';}
  function oraRoma(){try{var p=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date());
    return p.replace(' ','T').slice(0,16);}catch(e){return new Date().toISOString().slice(0,16);}}
  var MESI=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  var GIORNI=['domenica','lunedì','martedì','mercoledì','giovedì','venerdì','sabato'];
  function dataAsta(s){var d=new Date(s.slice(0,10)+'T12:00:00Z');return GIORNI[d.getUTCDay()]+' '+d.getUTCDate()+' '+MESI[d.getUTCMonth()]+' '+d.getUTCFullYear()+(s.length>10?', ore '+s.slice(11,16):'');}
  function letto(s){var d=new Date(s);if(isNaN(d))return s;
    try{var p=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).format(d);
      return (+p.slice(8,10))+' '+MESI[+p.slice(5,7)-1]+' '+p.slice(0,4)+' alle '+p.slice(11,16);}catch(e){return d.toLocaleString('it-IT');}}
  function scTesto(s){return s<=-3?'sotto la media OMI di zona':(s>=3?'sopra la media OMI di zona':'in linea con la media OMI di zona');}
  function scCls(s){return s<=-3?'down':(s>=3?'up':'neu');}
  var lotti=[].slice.call(document.querySelectorAll('[data-id]'));
  function aggiornaLotto(el,v){
    var base=v[0],min=v[1],data=v[2];
    if(base)el.dataset.base=base;if(min)el.dataset.min=min;if(data)el.dataset.data=data;
    var q=function(s){return el.querySelector(s);};
    if(base&&q('[data-v=base]'))q('[data-v=base]').textContent=eur(base);
    if(min&&q('[data-v=min]'))q('[data-v=min]').textContent=eur(min);
    if(data&&q('[data-v=data]'))q('[data-v=data]').textContent=dataAsta(data);
    var mq=+el.dataset.mq,omi=+el.dataset.omi;
    if(mq&&omi&&el.dataset.sc!==''&&min&&base){
      var s=Math.round((min/mq/omi-1)*100);el.dataset.sc=s;
      var sc=q('.sc');if(sc){sc.className='sc '+scCls(s);sc.querySelector('b').textContent=(s>0?'+':(s<0?'−':''))+Math.abs(s)+'%';sc.querySelector('span').textContent=scTesto(s);}
      if(q('[data-v=mqmin]'))q('[data-v=mqmin]').textContent=num(min/mq);
      if(q('[data-v=mqbase]'))q('[data-v=mqbase]').textContent=num(base/mq);
      var sca=q('.scala');if(sca){var mx=+sca.dataset.max;var a=q('.m.min'),bb=q('.m.base');
        if(a)a.style.left=Math.min(100,min/mq/mx*100).toFixed(1)+'%';if(bb)bb.style.left=Math.min(100,base/mq/mx*100).toFixed(1)+'%';}
    }
  }
  function conta(){
    document.querySelectorAll('[data-lista]').forEach(function(ls){
      var vis=[].slice.call(ls.querySelectorAll('[data-id]')).filter(function(e){return !e.hidden;}).length;
      var box=ls.closest('[data-blocco]')||ls.parentNode;
      box.querySelectorAll('[data-conta]').forEach(function(c){c.textContent=num(vis);});
      box.querySelectorAll('[data-plur]').forEach(function(c){var f=c.dataset.plur.split('|');c.textContent=vis===1?f[0]:f[1];});
      var vu=box.querySelector('[data-vuoto]');if(vu)vu.hidden=vis>0;
    });
    var nas=lotti.filter(function(e){return e.classList.contains('passato');}).length;
    document.querySelectorAll('[data-nascosti]').forEach(function(n){if(nas){n.hidden=false;n.textContent=' · '+(nas===1?'nascosta 1 asta già svolta o tolta dal PVP':'nascoste '+num(nas)+' aste già svolte o tolte dal PVP');}});
  }
  function filtra(){
    document.querySelectorAll('[data-lista]').forEach(function(ls){
      var f=ls.dataset.filtro||'tutti';
      [].forEach.call(ls.querySelectorAll('[data-id]'),function(e){
        var ok=!e.classList.contains('passato')&&(f==='tutti'||(f==='liberi'&&e.dataset.disp==='libero')||(f==='omi'&&e.dataset.sc!==''));
        e.hidden=!ok;});
    });
    conta();
  }
  function scadenze(){var ora=oraRoma();lotti.forEach(function(e){if(e.dataset.data&&e.dataset.data<ora)e.classList.add('passato');});}
  scadenze();filtra();
  var gen=document.body.dataset.gen,url=document.body.dataset.live;
  if(url&&lotti.length&&window.fetch){
    fetch(url,{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(L){
      if(!L||!L.lotti||!(Date.parse(L.letto_il)>Date.parse(gen)))return;
      lotti.forEach(function(e){var v=L.lotti[e.dataset.id];if(v)aggiornaLotto(e,v);else e.classList.add('passato');});
      document.querySelectorAll('[data-letto]').forEach(function(x){x.textContent=letto(L.letto_il);});
      scadenze();filtra();ordinaTutte();
    }).catch(function(){});
  }
  function ordina(ls,how){
    var el=[].slice.call(ls.children);
    el.sort(function(a,b){
      var da=a.dataset.data||'',db=b.dataset.data||'';
      if(how==='data')return da<db?-1:(da>db?1:0);
      if(how==='prezzo')return (+a.dataset.min||+a.dataset.base)-(+b.dataset.min||+b.dataset.base)||(da<db?-1:1);
      var sa=a.dataset.sc===''?null:+a.dataset.sc,sb=b.dataset.sc===''?null:+b.dataset.sc;
      if(sa===null&&sb===null)return da<db?-1:(da>db?1:0);if(sa===null)return 1;if(sb===null)return -1;return sa-sb||(da<db?-1:1);});
    el.forEach(function(e){ls.appendChild(e);});
  }
  function ordinaTutte(){document.querySelectorAll('[data-lista][data-ordine]').forEach(function(ls){ordina(ls,ls.dataset.ordine);});}
  document.querySelectorAll('[data-filtri]').forEach(function(g){var ls=document.getElementById(g.dataset.filtri);var bt=g.querySelectorAll('button');
    bt.forEach(function(x){x.addEventListener('click',function(){bt.forEach(function(y){y.setAttribute('aria-pressed','false');});x.setAttribute('aria-pressed','true');ls.dataset.filtro=x.dataset.f;filtra();});});});
  document.querySelectorAll('[data-ordina]').forEach(function(s){var ls=document.getElementById(s.dataset.ordina);
    s.addEventListener('change',function(){ls.dataset.ordine=s.value;ordina(ls,s.value);});});
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
CONTI = {}
AD = '<div class="ad-slot" aria-hidden="true"></div>'
MENU = [("citta/", "Città"), ("auto-all-asta/", "Auto all'asta"), ("guide/", "Guide"), ("metodologia/", "Metodo"), ("chi-siamo/", "Chi siamo")]


def pagina(percorso, titolo, descrizione, corpo, tipo, briciole=None, indicizza=True, assoluto=False, testata="", jsonld_extra=None):
    file = percorso if percorso.endswith(".html") else (percorso + "index.html")
    prof = file.count("/")
    rel = "/" if assoluto else ("../" * prof or "./")
    url_pag = URL_SITO + "/" + percorso
    if indicizza:
        URLS.append(percorso)
        CONTI[tipo] = CONTI.get(tipo, 0) + 1
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/", "inLanguage": "it-IT"}] if percorso == "" else []
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL_SITO + "/"}]
        for i, (n, p) in enumerate(briciole, start=2):
            voci.append({"@type": "ListItem", "position": i, "name": n, "item": URL_SITO + "/" + p})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Percorso"><a href="' + rel + '">Home</a>' +
              "".join(f' › <a href="{rel}{p}">{h(n)}</a>' for n, p in briciole[:-1]) + f" › {h(briciole[-1][0])}</nav>")
    if jsonld_extra:
        ld.append(jsonld_extra)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    menu = "".join(f'<a href="{rel}{u}"' + (' aria-current="page"' if percorso.startswith(u) else "") + f'>{t}</a>' for u, t in MENU)
    testata = testata.replace("{bc}", bc).replace("{rel}", rel)
    corpo = corpo.replace("{rel}", rel).replace("{bc}", bc)
    live = f' data-live="{URL_LIVE}"' if 'data-id="' in corpo else ""
    testo = f"""<!DOCTYPE html>
<html lang="it">
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
<meta property="og:locale" content="it_IT">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NOME}: case all'asta con prezzo, offerta minima e confronto con i valori OMI di zona">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1C2E2A">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<script>{TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body data-gen="{ADESSO.isoformat(timespec='minutes')}"{live}>
<a class="skip" href="#main">Vai al contenuto</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">{LOGO}<span>Aste <b>in Chiaro</b></span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<button type="button" class="tema" data-tema aria-label="Passa al tema chiaro o scuro">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Apri il menu">{ico("menu")}Menu</summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo}{riquadro_trasparenza(corpo)}
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{rel}">{LOGO}<span>Aste <b>in Chiaro</b></span></a>
<p><strong>{NOME}</strong> è un sito indipendente: non è collegato al Ministero della Giustizia, ai tribunali, ai professionisti delegati o all'Agenzia delle Entrate. Mostra i dati pubblici delle aste del <a href="{PVP}" rel="noopener">Portale delle Vendite Pubbliche</a> e, per confronto, le quotazioni immobiliari di zona.</p>
<p><strong>Non è consulenza legale, fiscale o finanziaria.</strong> Prima di fare un'offerta leggi l'avviso di vendita e la perizia sul PVP e chiedi al professionista delegato o al custode indicati nell'annuncio.</p>
<p class="small" style="color:inherit">Valori €/m² di zona: «{ATTRIB}», {SEM_TESTO}, licenza <a href="{CC_BY}" rel="noopener license">CC BY 4.0</a>. I valori OMI sono indicativi e non sostituiscono una stima.</p>
</div><div>
<h2>Esplora</h2>
<ul><li><a href="{rel}citta/">Tutte le città</a></li><li><a href="{rel}auto-all-asta/">Auto all'asta</a></li><li><a href="{rel}guide/">Guide</a></li><li><a href="{rel}metodologia/">Metodo e fonti</a></li><li><a href="{rel}chi-siamo/">Chi siamo</a></li><li><a href="{rel}contatti/">Contatti</a></li><li><a href="{rel}privacy.html">Privacy</a></li></ul>
</div></div>
<p class="f-base">Aste lette sul PVP il <span data-letto>{letto_testo(LETTO)}</span> · Prezzi e date si aggiornano ogni giorno, le pagine ogni settimana.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", icona="gavel"):
    return f"""<section class="band"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


# ---------------------------------------------------------------- componenti
def scheda(L, rel_zone=True):
    """Scheda di un lotto. Tutto quello che mostra viene dai campi strutturati del PVP; niente testo libero dell'annuncio."""
    k = (L["comune"], L["prov"])
    d_lab, d_cls, d_tit = DISP.get(L["disp"], DISP["nd"])
    badge = [f'<span class="badge {d_cls}" title="{h(d_tit)}">{h(d_lab)}</span>']
    if L.get("pubblicato") and L["pubblicato"] >= NUOVO_DAL:
        badge.insert(0, '<span class="badge b-new">Nuova</span>')
    if L.get("diritto") == "parziale":
        badge.append('<span class="badge b-quota" title="L\'annuncio parla di una quota o di un diritto diverso dalla piena proprietà">Quota o diritto parziale?</span>')
    if L.get("n_abitazioni", 0) > 1:
        badge.append(f'<span class="badge b-nd">{L["n_abitazioni"]} unità nello stesso lotto</span>')
    dove = h(L["comune"]) + (f" · {h(L['via'])}" if L.get("via") else "")
    zona_html = ""
    if L.get("zona"):
        cod, z = L["zona"]
        nz = nome_zona(cod, z)
        zz = zone_citta(k) if k in CITTA else {}
        lab = f"Zona OMI {h(z)} – {h(nz)}"
        if rel_zone and tuple(L["zona"]) in zz:
            zona_html = f'<small><a href="{{rel}}{url_zona(k, cod, z)}">{lab}</a></small>'
        else:
            zona_html = f"<small>{lab}</small>"
    elif L.get("via") is None:
        zona_html = "<small>Indirizzo e zona: vedi la scheda sul PVP</small>"
    info = [f'<li>{ico("calendar")}<span>Asta: <b data-v="data">{h(data_asta(L["data"]))}</b></span></li>']
    if L.get("termine"):
        info.append(f'<li>{ico("clock")}<span>Offerte entro il {h(data_lunga(L["termine"]))}' +
                    (f", ore {h(L['termine'][11:16])}" if len(L["termine"]) > 10 else "") + "</span></li>")
    mod = " · ".join(x for x in [L.get("tipo_vendita"), L.get("modalita")] if x)
    if mod:
        info.append(f'<li>{ico("gavel")}<span>{h(mod[:1].upper() + mod[1:].lower())}</span></li>')
    if L.get("tribunale"):
        info.append(f'<li>{ico("scale")}<span>Tribunale di {h(L["tribunale"])}</span></li>')
    # colonna OMI
    sc = L.get("sconto_min")
    O = L.get("omi")
    if sc is not None:
        mx = max(O[2], L["eur_mq_base"], L["eur_mq_min"]) * 1.12
        p = lambda v: f"{min(100, v / mx * 100):.1f}%"  # noqa: E731
        segno = "−" if sc < 0 else ("+" if sc > 0 else "")
        omi_html = f"""<p class="small">Confronto con la zona ({L['mq']} m²)</p>
<p class="sc {sconto_cls(sc)}"><b>{segno}{abs(sc)}%</b><span>{sconto_testo(sc)}</span></p>
<p class="det">Con l'offerta minima: <b><span data-v="mqmin">{intero(L['eur_mq_min'])}</span> €/m²</b> · col prezzo base: <span data-v="mqbase">{intero(L['eur_mq_base'])}</span> €/m².<br>
Media OMI della zona: <b>{intero(O[3])} €/m²</b> (da {intero(O[1])} a {intero(O[2])}, {h(O[0].lower())}, stato {h(O[4])}, {SEM_BREVE}).</p>
<div class="scala" data-max="{mx:.0f}" role="img" aria-label="Valori OMI della zona da {intero(O[1])} a {intero(O[2])} €/m²; il lotto costa {intero(L['eur_mq_min'])} €/m² con l'offerta minima">
<span class="t"></span><span class="r" style="left:{p(O[1])};width:calc({p(O[2])} - {p(O[1])})"></span>
<span class="m base" style="left:{p(L['eur_mq_base'])}"></span><span class="m min" style="left:{p(L['eur_mq_min'])}"></span></div>
<p class="leg"><span><i class="k1"></i>offerta minima</span><span><i class="k2"></i>prezzo base</span><span><i class="k3"></i>valori OMI di zona</span></p>"""
    else:
        if L.get("diritto") == "parziale":
            mot = ("Forse si vende una quota o un diritto parziale", "L'annuncio parla di una quota o di un diritto diverso dalla piena proprietà (per esempio nuda proprietà): controlla nell'avviso che cosa si vende. Il confronto €/m² non è calcolato.")
        elif not L.get("mq"):
            mot = ("Superficie non indicata", "L'annuncio non riporta i metri quadri in modo chiaro: niente €/m² e niente confronto. Li trovi nella perizia sul PVP.")
        elif L.get("mq_dubbio"):
            mot = (f"{L['mq']} m² nell'annuncio: dato da verificare", "Il prezzo al metro quadro risulterebbe troppo lontano dai valori della zona: forse la superficie si riferisce solo a una parte del lotto. Controlla la perizia.")
        elif L.get("cat") == "FABBRICATO_IN_COSTR":
            mot = (f"{L['mq']} m² · fabbricato in costruzione", "Per un edificio non finito il confronto con le case della zona non ha senso.")
        else:
            mot = (f"{L['mq']} m² · zona OMI non trovata", "Il PVP non dà le coordinate del bene (o non cadono in una zona OMI del comune): confronto non calcolato.")
        extra = ""
        if O and not L.get("diritto") == "parziale":
            extra = f'<p class="det">Per orientarti: media OMI della zona {intero(O[3])} €/m² ({h(O[0].lower())}, {SEM_BREVE}).</p>'
        omi_html = f'<p class="small">Confronto con la zona</p><div class="nocalc"><b>{h(mot[0])}</b>{h(mot[1])}</div>{extra}'
    attr = (f'data-id="{L["id"]}" data-data="{L["data"]}" data-base="{L["base"]}" data-min="{L["minima"]}" '
            f'data-mq="{L["mq"] if sc is not None else ""}" data-omi="{O[3] if sc is not None else ""}" '
            f'data-sc="{sc if sc is not None else ""}" data-disp="{L["disp"]}"')
    return f"""<li class="lotto" {attr}>
<div class="l-testa"><span class="l-tipo">{h(L['tipo'])}</span>{''.join(badge)}</div>
<h3 class="l-tit">{dove}{zona_html}</h3>
<div class="l-sx">
<div class="prezzi"><div class="pm"><span>Offerta minima</span><b data-v="min">{euro(L['minima'])}</b></div><div><span>Prezzo base</span><b data-v="base">{euro(L['base'])}</b></div></div>
<ul class="info">{''.join(info)}</ul>
</div>
<div class="omi">{omi_html}</div>
<div class="l-link"><a class="pvp" href="{PVP_LOTTO.format(L['id'])}" rel="noopener" target="_blank">{ico("ext")}Scheda ufficiale sul PVP (n. {L['id']})</a></div>
</li>"""


def elenco_lotti(lotti, id_lista, ordine="sconto", strumenti=True, rel_zone=True):
    lotti = ordina_sconto(lotti) if ordine == "sconto" else sorted(lotti, key=lambda L: (L["data"], L["id"]))
    n_omi = sum(1 for L in lotti if L.get("sconto_min") is not None)
    n_lib = sum(1 for L in lotti if L["disp"] == "libero")
    barra = ""
    if strumenti:
        barra = f"""<div class="strumenti">
<div class="filtri" role="group" aria-label="Filtra le aste" data-filtri="{id_lista}"><button type="button" data-f="tutti" aria-pressed="true">Tutte ({len(lotti)})</button><button type="button" data-f="liberi" aria-pressed="false">Solo libere ({n_lib})</button><button type="button" data-f="omi" aria-pressed="false">Con confronto €/m² ({n_omi})</button></div>
<label class="ordina">Ordina <select data-ordina="{id_lista}"><option value="sconto"{' selected' if ordine == 'sconto' else ''}>Sconto più alto sulla zona</option><option value="data"{' selected' if ordine == 'data' else ''}>Asta più vicina</option><option value="prezzo">Offerta minima più bassa</option></select></label>
</div>"""
    return f"""<div data-blocco>{barra}
<p class="conta"><b data-conta>{len(lotti)}</b> <span data-plur="asta in elenco|aste in elenco">{'asta in elenco' if len(lotti) == 1 else 'aste in elenco'}</span><span data-nascosti hidden></span></p>
<ul class="lotti" id="{id_lista}" data-lista data-ordine="{ordine}">{''.join(scheda(L, rel_zone) for L in lotti)}</ul>
<p class="vuoto" data-vuoto hidden>Nessuna asta da mostrare con questo filtro: le aste di questa pagina potrebbero essersi già svolte. Prova un altro filtro o torna dopo il prossimo aggiornamento.</p>
</div>"""


def statistiche(lotti):
    basi = [L["base"] for L in lotti]
    con = [L["sconto_min"] for L in lotti if L.get("sconto_min") is not None]
    lib = sum(1 for L in lotti if L["disp"] == "libero")
    sotto = sum(1 for s in con if s <= -3)
    cells = [
        (intero(len(lotti)), "case all'asta con vendita da oggi in poi"),
        (euro_breve(mediana(basi)), "prezzo base mediano"),
        (f"{intero(len(con))}", "con superficie e confronto con la zona OMI"),
        (f"{intero(lib)}", "libere secondo l'annuncio"),
    ]
    if con:
        cells[2] = (f"{intero(sotto)} su {intero(len(con))}", "sotto la media OMI di zona con l'offerta minima")
    return '<div class="stat-row">' + "".join(f'<div class="stat"><b>{a}</b><span>{b}</span></div>' for a, b in cells) + "</div>"


def agg_riga():
    return (f'<p class="agg">{ico("check")}<span>Aste lette sul PVP il <b data-letto>{letto_testo(LETTO)}</b>. '
            f'Prezzi e date si aggiornano ogni giorno: le aste già svolte spariscono da sole.</span></p>')


def box_mutuo():
    m = (AFFILIATI or {}).get("mutuo") or {}
    if not m.get("url"):
        return ""
    return f"""<aside class="mutuo-box" aria-label="Mutuo per l'asta"><div><p><strong>{h(m.get('titolo', ''))}</strong></p>
<p class="small">{h(m.get('testo', ''))} Link sponsorizzato{(' di ' + h(m['nome'])) if m.get('nome') else ''}: non cambia i dati di questa pagina. {MON.RIGA_IT}</p></div>
<a class="btn" href="{h(m['url'])}" rel="sponsored noopener" target="_blank">{h(m.get('bottone', 'Scopri'))}</a></aside>"""


AVVISO = (f'<p class="nota">{ico("info")}<strong>Sono fatti, non consigli.</strong> Lo sconto confronta il prezzo al metro quadro con la media OMI '
          f'della zona, che è un valore indicativo: lo stato della casa, gli abusi, le spese e l\'occupazione possono cambiare tutto. '
          f'Prima di offrire leggi avviso e perizia sul PVP e chiedi al professionista delegato. <a href="{{rel}}guide/rischi-casa-all-asta/">I rischi da conoscere</a>.</p>')


def fonti_box(zona_cod=None):
    extra = ""
    return f"""<aside class="fonti-box" aria-label="Fonti"><h2>{ico("db")}Da dove vengono questi numeri</h2>
<ul><li><strong>Aste</strong>: <a href="{PVP}" rel="noopener">Portale delle Vendite Pubbliche</a> (Ministero della Giustizia), campi pubblici di ogni lotto: prezzo base, offerta minima, data, comune, stato di occupazione, coordinate. Letti il {letto_testo(LETTO)}; prezzi e date si aggiornano ogni giorno.</li>
<li><strong>Valori di zona</strong>: «{ATTRIB}», quotazioni del {SEM_TESTO} (consultazione pubblica <a href="{OMI_GEOPOI}" rel="noopener">GEOPOI</a>), licenza <a href="{CC_BY}" rel="noopener license">CC BY 4.0</a>. Media = metà strada tra valore minimo e massimo della tipologia più vicina al lotto, stato conservativo normale.{extra}</li>
<li><strong>Superficie</strong>: solo se l'annuncio scrive i metri quadri in modo chiaro. Altrimenti: «superficie non indicata» e nessun €/m².</li></ul>
<p>Dettagli e limiti nella pagina <a href="{{rel}}metodologia/">Metodo e fonti</a>. Non pubblichiamo nomi, contatti o documenti delle procedure: per tutto il resto c'è il link alla scheda ufficiale.</p></aside>"""


# ---------------------------------------------------------------- pagine città, fascia, zona
def frase_citta(nome, lotti):
    basi = sorted(L["base"] for L in lotti)
    date_ = sorted(L["data"] for L in lotti)
    con = [L["sconto_min"] for L in lotti if L.get("sconto_min") is not None]
    periodo = (f", tutte con vendita il {data_lunga(date_[0])}" if date_[0][:10] == date_[-1][:10]
               else f" con vendita tra il {data_lunga(date_[0])} e il {data_lunga(date_[-1])}")
    s = (f"A {h(nome)} ci sono <strong>{plur(len(lotti), 'casa', 'case')} all'asta</strong>{periodo}. "
         f"Il prezzo base va da {euro(basi[0])} a {euro(basi[-1])}")
    s += f", con un valore centrale di {euro(mediana(basi))}." if len(basi) > 2 else "."
    if len(con) >= 3:
        m = round(mediana(con))
        if abs(m) < 3:
            coda = "metà di questi costa al metro quadro meno della media di zona, metà di più: nel complesso in linea." if m <= 0 else \
                   "metà di questi costa al metro quadro più della media di zona, metà di meno: nel complesso in linea."
        else:
            art = "l'" if abs(m) in (1, 11) or str(abs(m)).startswith("8") else "il "
            coda = f"metà di questi costa al metro quadro almeno {art}{abs(m)}% {'in meno' if m < 0 else 'in più'} della media di zona."
        s += f" Per {plur(len(con), 'lotto', 'lotti')} l'annuncio indica la superficie e c'è una zona OMI: con l'offerta minima, {coda}"
    elif con:
        s += f" Solo per {plur(len(con), 'lotto', 'lotti')} si può calcolare il confronto con la media OMI di zona."
    else:
        s += " Per nessun lotto l'annuncio permette un confronto €/m² affidabile con la media OMI di zona."
    return s


def pagina_citta(k):
    nome, prov = k
    lotti = CITTA[k]
    u = url_citta(k)
    zz = zone_citta(k)
    ff = fasce_citta(k)
    nav = ""
    if ff:
        nav += "<h2>Per fascia di prezzo</h2><ul class=\"chips\">" + "".join(
            f'<li><a href="{{rel}}{u}{f[0]}/">{h(f[1])} <small>{len(v)}</small></a></li>' for f, v in ff) + "</ul>"
    if zz:
        nav += "<h2>Per zona OMI</h2><ul class=\"chips\">" + "".join(
            f'<li><a href="{{rel}}{url_zona(k, c, z)}">{h(nome_zona(c, z))} <small>{len(v)}</small></a></li>'
            for (c, z), v in sorted(zz.items(), key=lambda kv: -len(kv[1]))) + "</ul>"
    corpo = f"""<div class="pull">{statistiche(lotti)}</div>{agg_riga()}
<p class="lead" style="margin-top:22px">{frase_citta(nome, lotti)}</p>
{nav}
<h2>Tutte le case all'asta a {h(nome)}</h2>
{AVVISO}
{elenco_lotti(lotti, "lista")}
{box_mutuo()}{AD}
<h2>Prima di offrire</h2>
<ul class="guide">{voci_guide(['come-funziona-asta-giudiziaria', 'offerta-minima', 'casa-occupata-all-asta', 'rischi-casa-all-asta'])}</ul>
{fonti_box()}"""
    testata = banda(f"Case all'asta · {prov}", f"Case all'asta a {nome}",
                    f"Prezzo base, offerta minima, data e stato di occupazione di ogni lotto del Portale delle Vendite Pubbliche, "
                    f"con il prezzo al metro quadro confrontato con la <strong>media OMI della zona</strong>.", icona="pin")
    pagina(u, f"Case all'asta a {nome}: prezzi e confronto OMI | {NOME}",
           f"{len(lotti)} case all'asta a {nome} dal Portale delle Vendite Pubbliche: prezzo base, offerta minima, data, "
           f"occupazione e €/m² rispetto alla media OMI di zona. Aggiornato ogni giorno.",
           corpo, "città", briciole=[("Città", "citta/"), (nome, u)], testata=testata)
    for f, v in ff:
        pagina_fascia(k, f, v)
    for (c, z), v in zz.items():
        pagina_zona(k, c, z, v)


def pagina_fascia(k, f, lotti):
    nome, prov = k
    u = url_citta(k) + f[0] + "/"
    altre = [x for x in fasce_citta(k) if x[0][0] != f[0]]
    corpo = f"""<div class="pull">{statistiche(lotti)}</div>{agg_riga()}
<p class="lead" style="margin-top:22px">Case all'asta a {h(nome)} con <strong>prezzo base {h(f[1])}</strong>. L'offerta minima può essere fino a un quarto più bassa del prezzo base: è indicata in ogni scheda.
Tutte le aste della città sono nella pagina <a href="{{rel}}{url_citta(k)}">Case all'asta a {h(nome)}</a>.</p>
{('<ul class="chips">' + ''.join(f'<li><a href="{{rel}}{url_citta(k)}{x[0][0]}/">{h(x[0][1])} <small>{len(x[1])}</small></a></li>' for x in altre) + '</ul>') if altre else ''}
<h2>Aste a {h(nome)} {h(f[1])}</h2>
{AVVISO}
{elenco_lotti(lotti, "lista")}
{box_mutuo()}{AD}
{fonti_box()}"""
    testata = banda(f"{nome} · fascia di prezzo", f"Case all'asta a {nome} {f[1]}",
                    "Aste del Portale delle Vendite Pubbliche in questa fascia di prezzo, con offerta minima, data, occupazione e confronto con la media OMI di zona.", icona="tag")
    pagina(u, f"Case all'asta a {nome} {f[1]} | {NOME}",
           f"{len(lotti)} case all'asta a {nome} con prezzo base {f[1]}: offerta minima, data, stato di occupazione e confronto con i valori OMI di zona.",
           corpo, "fascia", briciole=[("Città", "citta/"), (nome, url_citta(k)), (f[1].capitalize(), u)], testata=testata)


def tabella_omi_zona(cod, z):
    Z = OMI["comuni"][cod]["zone"][z]
    righe = []
    for tip, stati in Z["valori"].items():
        for st, (a, b, sup, prev) in stati.items():
            righe.append(f'<tr><td>{h(tip)}</td><td data-l="Stato">{h(st.rstrip("*").lower())}</td>'
                         f'<td class="n" data-l="Da">{intero(a)}</td><td class="n" data-l="A">{intero(b)}</td>'
                         f'<td class="n" data-l="Media">{intero((a + b) / 2)}</td><td data-l="Superficie">{"lorda" if sup == "L" else "netta"}</td></tr>')
    return f"""<div class="tab"><table class="ct"><caption class="small" style="text-align:left;padding:10px 12px">Valori di compravendita in €/m², zona {h(z)}, {SEM_TESTO}. Fonte: «{ATTRIB}» (CC BY 4.0).</caption>
<thead><tr><th>Tipologia</th><th>Stato</th><th class="n">Da €/m²</th><th class="n">A €/m²</th><th class="n">Media</th><th>Superficie</th></tr></thead>
<tbody>{''.join(righe)}</tbody></table></div>"""


def pagina_zona(k, cod, z, lotti):
    nome, prov = k
    Z = OMI["comuni"][cod]["zone"][z]
    nz = nome_zona(cod, z)
    u = url_zona(k, cod, z)
    fascia = {"B": "centrale", "C": "semicentrale", "D": "periferica", "E": "suburbana", "R": "extraurbana/rurale"}.get(Z.get("fascia"), "")
    corpo = f"""<div class="pull">{statistiche(lotti)}</div>{agg_riga()}
<p class="lead" style="margin-top:22px">La zona OMI <strong>{h(z)}</strong> di {h(nome)}, «{h(nome_zona(cod, z, breve=False))}»{', in fascia ' + fascia + ',' if fascia else ''} è una delle zone in cui
l'Agenzia delle Entrate divide il comune per pubblicare le quotazioni immobiliari. Qui sotto trovi le aste che cadono in questa zona e i valori OMI con cui le confrontiamo.</p>
<h2>Aste nella zona {h(nz)}</h2>
{AVVISO}
{elenco_lotti(lotti, "lista", rel_zone=False)}
<h2>Quotazioni OMI della zona {h(z)}</h2>
<p class="lead">Tipologia prevalente nella zona: {h((Z.get('prevalente') or 'non indicata').lower())}. Le quotazioni sono intervalli indicativi, non stime di singole case.</p>
{tabella_omi_zona(cod, z)}
<p class="small">Tutte le aste della città: <a href="{{rel}}{url_citta(k)}">Case all'asta a {h(nome)}</a>.</p>
{box_mutuo()}{AD}
{fonti_box()}"""
    testata = banda(f"{nome} · zona OMI {z}", f"Case all'asta a {nome}, zona {nz}",
                    f"Aste del Portale delle Vendite Pubbliche nella zona OMI {h(z)}, con il prezzo al metro quadro confrontato con le quotazioni della zona ({SEM_TESTO}).", icona="pin")
    pagina(u, f"Case all'asta a {nome}, zona {nz} | {NOME}",
           f"{len(lotti)} case all'asta a {nome} nella zona OMI {z} ({nz}): prezzo base, offerta minima, data, occupazione e quotazioni OMI della zona.",
           corpo, "zona", briciole=[("Città", "citta/"), (nome, url_citta(k)), (f"Zona {nz}", u)], testata=testata)


# ---------------------------------------------------------------- home e indice città
PRIORITA = ["Roma", "Milano", "Napoli", "Torino", "Palermo", "Genova", "Bologna", "Firenze", "Bari", "Catania", "Venezia", "Verona",
            "Messina", "Padova", "Trieste", "Brescia", "Taranto", "Parma", "Prato", "Modena", "Reggio di Calabria", "Reggio nell'Emilia",
            "Perugia", "Ravenna", "Livorno", "Cagliari", "Foggia", "Rimini", "Salerno", "Ferrara", "Sassari", "Latina", "Monza", "Siracusa",
            "Pescara", "Bergamo", "Forlì", "Trento", "Vicenza", "Terni", "Bolzano", "Novara", "Piacenza", "Ancona", "Andria", "Arezzo"]


def citta_ordinate():
    """Prima le città più grandi d'Italia (per abitanti), poi le altre per numero di aste."""
    pos = {norm(c): i for i, c in enumerate(PRIORITA)}
    return sorted(CITTA, key=lambda k: (pos.get(norm(k[0]), 999), -len(CITTA[k]), norm(k[0])))


def home():
    tutte = LOTTI
    grandi = citta_ordinate()
    blocchi = []
    for k in grandi:
        con = [L for L in ordina_sconto(CITTA[k]) if L.get("sconto_min") is not None]
        recenti = [L for L in con if (L.get("pubblicato") or "") >= RECENTI_DAL]
        top = (recenti + [L for L in con if L not in recenti])[:2]
        if len(top) < 2:
            continue
        blocchi.append(f"""<section class="cittablocco" data-blocco><div class="tit"><h3>{h(k[0])}</h3><a href="{{rel}}{url_citta(k)}">Tutte le {len(CITTA[k])} aste a {h(k[0])} {ico("arrow")}</a></div>
<ul class="lotti" data-lista data-ordine="sconto">{''.join(scheda(L) for L in top)}</ul>
<p class="vuoto" data-vuoto hidden>Le aste in evidenza si sono già svolte: le altre sono nella <a href="{{rel}}{url_citta(k)}">pagina di {h(k[0])}</a>.</p></section>""")
        if len(blocchi) == 8:
            break
    chips = "".join(f'<li><a href="{{rel}}{url_citta(k)}">{h(k[0])} <small>{len(CITTA[k])}</small></a></li>' for k in grandi[:24])
    con = [L for L in tutte if L.get("sconto_min") is not None]
    corpo = f"""<div class="pull">{statistiche(tutte)}</div>{agg_riga()}
<h2>Scegli la città</h2>
<ul class="chips">{chips}<li><a href="{{rel}}citta/">Tutte le {len(CITTA)} città {ico("arrow")}</a></li></ul>
<h2>Sotto la media di zona: le aste con lo sconto più alto</h2>
<p class="lead">Per ogni città, tra le aste pubblicate nelle ultime tre settimane, i lotti in cui l'<strong>offerta minima</strong> al metro quadro è più lontana dalla media OMI della zona (se non bastano, anche aste meno recenti). Accanto trovi sempre lo stato di occupazione e il link alla scheda ufficiale.</p>
{AVVISO}
{''.join(blocchi)}
{AD}
<h2>Come leggere una scheda</h2>
<ol class="passi"><li><b>Prezzo base e offerta minima</b><p>Il prezzo base lo fissa il giudice partendo dalla stima. L'offerta minima può essere fino al 25% più bassa: sotto non si può offrire.</p></li>
<li><b>Confronto con la zona</b><p>Dividiamo il prezzo per i metri quadri scritti nell'annuncio e lo confrontiamo con la media OMI della zona ({SEM_BREVE}). Se i metri quadri mancano, niente confronto.</p></li>
<li><b>Occupazione e scheda ufficiale</b><p>Libero, occupato o non indicato: lo dice il PVP. Avviso, perizia, visita e offerta passano tutti dalla scheda ufficiale.</p></li></ol>
<h2>Guide in parole semplici</h2>
<ul class="guide">{voci_guide([g[0] for g in GUIDE])}</ul>
<h2>Anche veicoli</h2>
<p class="lead">Auto, moto e furgoni messi all'asta dai tribunali, con prezzo base e data: <a href="{{rel}}auto-all-asta/">auto all'asta in tutta Italia</a> ({intero(len(VEICOLI))} veicoli).</p>
{fonti_box()}"""
    testata = banda("Aste giudiziarie · dati pubblici", "Case all'asta: prezzo, offerta minima e confronto con la zona",
                    f"Le aste di case del Portale delle Vendite Pubbliche in {len(CITTA)} città, con il prezzo al metro quadro messo accanto alla "
                    f"<strong>media OMI di zona</strong> dell'Agenzia delle Entrate. Solo fatti: prezzi, date, occupazione e link alla scheda ufficiale.",
                    extra=f'<ul class="trust"><li>{ico("check")}Aggiornato ogni giorno</li><li>{ico("shield")}Nessun dato personale</li><li>{ico("doc")}Link alla scheda ufficiale</li></ul>',
                    icona="house")
    pagina("", f"Case all'asta sotto la media di zona: prezzi e valori OMI | {NOME}",
           f"Case all'asta in {len(CITTA)} città dal Portale delle Vendite Pubbliche: prezzo base, offerta minima, data, occupazione e "
           f"€/m² confrontato con la media OMI di zona. Aggiornato ogni giorno, senza dati personali.",
           corpo, "home", testata=testata)


def conf_testo(n):
    return "nessun confronto €/m²" if n == 0 else f"{intero(n)} con confronto €/m²"


def pagina_indice_citta():
    per_reg = {}
    for k, v in CITTA.items():
        reg = next((L.get("regione") for L in v if L.get("regione")), None) or "Altre"
        per_reg.setdefault(reg, []).append(k)
    sezioni = []
    for reg in sorted(per_reg, key=lambda r: (r == "Altre", norm(r))):
        voci = sorted(per_reg[reg], key=lambda k: norm(k[0]))
        sezioni.append(f'<h2>{h(reg)}</h2><ul class="griglia">' + "".join(
            f'<li><a href="{{rel}}{url_citta(k)}"><span>{h(k[0])} <small>({h(k[1])})</small></span>'
            f'<small>{plur(len(CITTA[k]), "asta", "aste")} · {conf_testo(sum(1 for L in CITTA[k] if L.get("sconto_min") is not None))}</small></a></li>'
            for k in voci) + "</ul>")
    corpo = f"""<div class="pull card"><p style="margin:0">Una pagina per ogni comune con almeno {SOGLIA_CITTA} case all'asta attive sul Portale delle Vendite Pubbliche.
Dentro: tutte le aste del comune, le fasce di prezzo e le zone OMI con più lotti. I comuni più piccoli o con poche aste non hanno ancora una pagina: le loro aste sono sul <a href="{PVP}" rel="noopener">PVP</a>.</p></div>
{''.join(sezioni)}
{fonti_box()}"""
    testata = banda("Città", "Case all'asta per città", f"{len(CITTA)} comuni, {intero(len(LOTTI))} aste di case con vendita da oggi in poi.", icona="pin")
    pagina("citta/", f"Case all'asta per città | {NOME}",
           f"Elenco dei {len(CITTA)} comuni con case all'asta sul Portale delle Vendite Pubbliche, con il numero di aste e il confronto con i valori OMI di zona.",
           corpo, "indice", briciole=[("Città", "citta/")], testata=testata)


# ---------------------------------------------------------------- veicoli
VEICOLI = [v for v in AUTO_J.get("veicoli", []) if v["data"] >= ADESSO.strftime("%Y-%m-%dT%H:%M")]
LIMITE_VEICOLI = 40  # per tipo, le aste più vicine (la pagina resta leggera)


def pagina_auto():
    tipi = ["Automobile", "Moto o ciclomotore", "Veicolo commerciale", "Veicolo"]
    plurali = {"Automobile": "Automobili", "Moto o ciclomotore": "Moto e ciclomotori", "Veicolo commerciale": "Veicoli commerciali", "Veicolo": "Altri veicoli"}
    sezioni = []
    for t in tipi:
        vv = sorted([v for v in VEICOLI if v["tipo"] == t], key=lambda v: (v["data"], v["id"]))
        if not vv:
            continue
        righe = []
        for v in vv[:LIMITE_VEICOLI]:
            nome = h(t) + (f" {h(v['marca'])}" if v.get("marca") else "") + (f" ({v['anno']})" if v.get("anno") else "")
            righe.append(f"""<tr data-id="{v['id']}" data-data="{v['data']}" data-base="{v['base']}" data-min="{v.get('minima') or ''}" data-sc="" data-disp="">
<td><a href="{PVP_LOTTO.format(v['id'])}" rel="noopener" target="_blank">{nome}</a><br><span class="small">{h(v['comune'])} ({h(v['prov'] or '')})</span></td>
<td class="n" data-l="Prezzo base"><span data-v="base">{euro(v['base'])}</span></td><td class="n" data-l="Offerta minima"><span data-v="min">{euro(v.get('minima'))}</span></td>
<td data-l="Asta"><span data-v="data">{h(data_asta(v['data']))}</span></td><td data-l="Tribunale">{h(v.get('tribunale') or '–')}</td></tr>""")
        altri = len(vv) - LIMITE_VEICOLI
        sezioni.append(f"""<section data-blocco><h2>{plurali[t]} <small class="small">({intero(len(vv))} in tutto{f", qui le {LIMITE_VEICOLI} aste più vicine" if len(vv) > LIMITE_VEICOLI else ""})</small></h2>
<div class="tab"><table class="ct"><thead><tr><th>Veicolo e luogo</th><th class="n">Prezzo base</th><th class="n">Offerta minima</th><th>Asta</th><th>Tribunale</th></tr></thead>
<tbody data-lista>{''.join(righe)}</tbody></table></div>
<p class="vuoto" data-vuoto hidden>Le aste di questo elenco si sono già svolte: torna dopo il prossimo aggiornamento.</p>
{f'<p class="small">Mostriamo le {LIMITE_VEICOLI} aste più vicine; altre {intero(altri)} sono sul <a href="{PVP}" rel="noopener">PVP</a> (ricerca «Mobili», categoria «Autoveicoli e cicli»).</p>' if altri > 0 else ''}</section>""")
    corpo = f"""<div class="pull card"><p style="margin:0"><strong>{intero(len(VEICOLI))} veicoli all'asta</strong> in tutta Italia sul Portale delle Vendite Pubbliche, dalle aste più vicine.
Per i veicoli non esiste un valore ufficiale di zona come l'OMI: mostriamo solo prezzo base, offerta minima, data e tribunale. Marca e anno, quando ci sono, vengono dal titolo dell'annuncio; la targa e il resto della descrizione non li pubblichiamo.</p></div>
{agg_riga()}
<p class="small">Un trattino al posto dell'offerta minima vuol dire che il PVP non la indica: vale quanto scritto nell'avviso di vendita.</p>
<p class="nota">{ico("info")}<strong>Prima di offrire</strong> leggi l'avviso sul PVP: spesso il veicolo si vede solo su appuntamento, si compra «visto e piaciuto», senza garanzia, e ritiro, passaggio di proprietà ed eventuali fermi o revisioni sono a carico di chi compra.</p>
{''.join(sezioni)}
{AD}
<aside class="fonti-box" aria-label="Fonti"><h2>{ico("db")}Da dove vengono questi dati</h2><p><a href="{PVP}" rel="noopener">Portale delle Vendite Pubbliche</a>, lotti della categoria «Autoveicoli e cicli» con vendita da oggi in poi, letti il {letto_testo(LETTO)}. Prezzi e date si aggiornano ogni giorno.</p></aside>"""
    testata = banda("Veicoli all'asta", "Auto all'asta dai tribunali, in tutta Italia",
                    "Automobili, moto e veicoli commerciali in vendita sul Portale delle Vendite Pubbliche: prezzo base, offerta minima, data dell'asta e link alla scheda ufficiale.", icona="car")
    pagina("auto-all-asta/", f"Auto all'asta dai tribunali: prezzi e date | {NOME}",
           f"{intero(len(VEICOLI))} auto, moto e veicoli commerciali all'asta sul Portale delle Vendite Pubbliche: prezzo base, offerta minima, data e tribunale. Aggiornato ogni giorno.",
           corpo, "auto", briciole=[("Auto all'asta", "auto-all-asta/")], testata=testata)


# ---------------------------------------------------------------- guide
def cpc(n, testo=None):
    return f'<a href="{NORMATTIVA_CPC.format(n.replace("-", ""))}" rel="noopener">{testo or "art. " + n + " c.p.c."}</a>'


def cc(n, testo=None):
    return f'<a href="{NORMATTIVA_CC.format(n)}" rel="noopener">{testo or "art. " + n + " c.c."}</a>'


GUIDE = [
    ("come-funziona-asta-giudiziaria", "Come funziona un'asta giudiziaria",
     "Dalla perizia al decreto di trasferimento: i passaggi, i tempi e chi fa cosa, spiegati semplice."),
    ("offerta-minima", "Cosa vuol dire offerta minima",
     "Prezzo base, offerta minima, rilancio e ribassi: perché l'asta può chiudersi al 75% del prezzo."),
    ("casa-occupata-all-asta", "Casa occupata all'asta: cosa sapere",
     "Chi libera la casa, quando, e quando un contratto d'affitto resta valido anche per chi compra."),
    ("rischi-casa-all-asta", "I rischi di comprare casa all'asta",
     "Niente garanzia per i vizi, abusi edilizi, spese condominiali, tempi: cosa controllare prima."),
    ("mutuo-casa-all-asta", "Mutuo per una casa all'asta",
     "Si può pagare il saldo con un mutuo: come funziona e perché va preparato prima dell'asta."),
    ("valori-omi", "Cosa sono i valori OMI",
     "Le quotazioni dell'Agenzia delle Entrate: cosa misurano, cosa no, e come le usiamo in questo sito."),
]


def voci_guide(slugs):
    d = {g[0]: g for g in GUIDE}
    return "".join(f'<li><a href="{{rel}}guide/{d[s][0]}/"><b>{h(d[s][1])}</b><span>{h(d[s][2])}</span></a></li>' for s in slugs)


DISCLAIMER_GUIDA = (f'<div class="avviso"><b>Informazioni generali, non consulenza legale.</b> Ogni procedura ha le sue regole, scritte '
                    f'nell\'ordinanza e nell\'avviso di vendita: valgono quelle. Per un caso concreto chiedi al professionista delegato, al custode '
                    f'o a un avvocato. Articoli di legge riletti su Normattiva il {data_lunga(CONTROLLO_NORME)}.</div>')


def testo_guida(s):
    if s == "come-funziona-asta-giudiziaria":
        return f"""<p class="lead">Un'asta giudiziaria è il modo in cui un tribunale vende un bene pignorato (o di un fallimento) per pagare i creditori. Per le case quasi tutto passa dal <a href="{PVP}" rel="noopener">Portale delle Vendite Pubbliche</a> (PVP) del Ministero della Giustizia, dove per legge va pubblicato ogni avviso di vendita ({cpc('490')}).</p>
<div class="indice"><b>In questa guida</b><ol><li>Chi organizza la vendita</li><li>Perizia, prezzo base e avviso</li><li>Come si fa un'offerta</li><li>Il giorno dell'asta</li><li>Dopo l'aggiudicazione</li></ol></div>
<h2>1. Chi organizza la vendita</h2>
<p>Il giudice dell'esecuzione di solito delega le operazioni a un <strong>professionista delegato</strong> (notaio, avvocato o commercialista, {cpc('591-bis')}) e nomina un <strong>custode</strong> che gestisce la casa e accompagna le visite. I loro contatti sono nella scheda del PVP: noi non li ripubblichiamo.</p>
<h2>2. Perizia, prezzo base e avviso</h2>
<p>Un esperto nominato dal giudice stima la casa e scrive la <strong>perizia</strong>: superficie, stato, conformità urbanistica e catastale, occupazione, vincoli. Con l'ordinanza di vendita il giudice fissa il <strong>prezzo base</strong>, l'<strong>offerta minima</strong>, la cauzione, il termine per le offerte e quello per pagare il saldo, che non può superare i <strong>120 giorni dall'aggiudicazione</strong> ({cpc('569')}).</p>
<p>Tutto questo è riassunto nell'<strong>avviso di vendita</strong>, che trovi con la perizia e le foto nella scheda del PVP. Leggerli entrambi è il primo passo, prima di qualsiasi calcolo.</p>
<h2>3. Come si fa un'offerta</h2>
<ul><li><strong>Chi può offrire</strong>: tutti tranne il debitore, di persona o tramite procuratore; un avvocato può offrire anche «per persona da nominare» ({cpc('571')}, {cpc('579')}).</li>
<li><strong>Quanto</strong>: almeno l'offerta minima, cioè il prezzo base meno un quarto al massimo ({cpc('571')}). Sotto quella cifra l'offerta non è efficace.</li>
<li><strong>Cauzione</strong>: almeno un decimo del prezzo che offri, nei modi indicati dall'avviso ({cpc('571')}).</li>
<li><strong>Come</strong>: oggi quasi sempre in modo telematico, con il modulo «Offerta telematica» raggiungibile dalla scheda del PVP ({cpc('569')}, quarto comma; regole tecniche nel <a href="{NORMATTIVA_DM32}" rel="noopener">D.M. 32/2015</a>). L'avviso dice se la vendita è sincrona, asincrona o mista.</li>
<li><strong>L'offerta è irrevocabile</strong>, salvo i casi previsti dalla legge ({cpc('571')}).</li></ul>
<p>Prima di offrire puoi <strong>visitare la casa</strong>: la richiesta si fa dal PVP, con il pulsante di prenotazione della visita nella scheda (<a href="{PVP_GUIDA}" rel="noopener">guida al PVP</a>).</p>
<h2>4. Il giorno dell'asta</h2>
<p>Il delegato apre le offerte. Se c'è <strong>una sola offerta</strong> pari o superiore al prezzo base, è accolta; se è più bassa ma non oltre un quarto, può essere accolta se non c'è una seria possibilità di vendere a un prezzo più alto e nessun creditore ha chiesto l'assegnazione ({cpc('572')}). Se le offerte sono <strong>più di una</strong>, si fa una gara partendo dall'offerta più alta ({cpc('573')}), con i rilanci minimi indicati nell'avviso.</p>
<p>Se nessuno offre, l'asta va <strong>deserta</strong> e il giudice può fissare un nuovo tentativo con un prezzo base più basso, fino a un quarto in meno; dopo il quarto tentativo andato deserto, fino alla metà ({cpc('591')}).</p>
<h2>5. Dopo l'aggiudicazione</h2>
<p>Chi vince versa il <strong>saldo</strong> entro il termine dell'avviso, anche con un mutuo ({cpc('585')}; vedi la <a href="{{rel}}guide/mutuo-casa-all-asta/">guida al mutuo</a>). Poi il giudice emette il <strong>decreto di trasferimento</strong>, che rende proprietario chi ha comprato e ordina di cancellare pignoramenti e ipoteche ({cpc('586')}). Imposte e spese del trasferimento sono a carico di chi compra: l'avviso dice come si calcolano.</p>
<p>Fonti generali: <a href="{MG_VENDITE}" rel="noopener">Ministero della Giustizia – Vendite giudiziarie</a>, <a href="{PVP_GUIDA}" rel="noopener">Guida al Portale delle Vendite Pubbliche</a>.</p>"""
    if s == "offerta-minima":
        return f"""<p class="lead">Nella scheda di ogni asta ci sono due prezzi: il <strong>prezzo base</strong> e l'<strong>offerta minima</strong>. La differenza tra i due è il motivo per cui un'asta può chiudersi sotto il prezzo scritto in grande.</p>
<h2>Prezzo base</h2>
<p>È il valore dell'immobile fissato dal giudice nell'ordinanza di vendita o dal professionista delegato, partendo dalla stima della perizia ({cpc('568')}, {cpc('569')}, {cpc('591-bis')}). Se arriva un'offerta pari o superiore al prezzo base, è accolta ({cpc('572')}).</p>
<h2>Offerta minima</h2>
<p>È la cifra più bassa che puoi offrire. Per legge un'offerta non è efficace se è inferiore <strong>di oltre un quarto</strong> al prezzo stabilito nell'ordinanza ({cpc('571')}). Quindi l'offerta minima è di solito il <strong>75% del prezzo base</strong>: con un prezzo base di 100.000 €, l'offerta minima è 75.000 €.</p>
<div class="avviso"><b>Attenzione: offrire il minimo non garantisce di comprare.</b> Con una sola offerta tra minimo e prezzo base, il delegato può non accettarla se ritiene possibile vendere a un prezzo più alto con una nuova asta, o se un creditore ha chiesto di farsi assegnare la casa ({cpc('572')}). E se ci sono altri offerenti si va a una gara ({cpc('573')}).</div>
<p>Su alcuni annunci del PVP l'offerta minima risulta <strong>uguale</strong> al prezzo base. Può essere una scelta dell'ordinanza o un errore di inserimento: fa fede l'avviso di vendita.</p>
<h2>Rilancio minimo</h2>
<p>Se c'è una gara tra più offerenti, ogni rilancio deve superare il precedente almeno della cifra indicata nell'avviso («rilancio minimo» o «aumento minimo»).</p>
<h2>Perché i prezzi scendono a ogni asta</h2>
<p>Se un'asta va deserta, il prezzo base del tentativo successivo può essere ridotto fino a un quarto; dopo il quarto tentativo deserto, fino alla metà ({cpc('591')}). Per questo una casa al terzo o quarto tentativo può avere un'offerta minima molto più bassa della stima iniziale. Il numero del tentativo è scritto nell'avviso di vendita.</p>
<h2>Come lo usiamo in questo sito</h2>
<p>Lo «sconto» che mostriamo confronta il <strong>prezzo al metro quadro con l'offerta minima</strong> con la media OMI della zona: è il prezzo più basso a cui la casa potrebbe essere venduta. Accanto c'è sempre anche il confronto col prezzo base. Dettagli in <a href="{{rel}}metodologia/">Metodo e fonti</a>.</p>"""
    if s == "casa-occupata-all-asta":
        return f"""<p class="lead">Nella scheda del PVP ogni bene ha uno stato: <strong>libero</strong>, <strong>occupato</strong>, <strong>occupato senza titolo</strong>, <strong>in corso di liberazione</strong> o <strong>non specificato</strong>. Cambia molto i tempi e i costi per entrare in casa.</p>
<h2>Occupata dal debitore e dalla sua famiglia</h2>
<p>Il debitore e i familiari che vivono con lui possono restare in casa fino al <strong>decreto di trasferimento</strong>, salvo casi particolari ({cpc('560')}). Con il decreto il giudice ordina la liberazione, che è attuata dal <strong>custode</strong>, nell'interesse e <strong>senza spese per chi ha comprato</strong>, a meno che chi compra non esoneri il custode ({cpc('560')}). Anche il decreto di trasferimento contiene l'ordine di rilascio ({cpc('586')}).</p>
<h2>Occupata da altri senza titolo, o non abitata</h2>
<p>Se la casa non è abitata dal debitore o è occupata da qualcuno senza un titolo valido contro la procedura, il giudice ordina la liberazione <strong>al più tardi</strong> quando autorizza la vendita ({cpc('560')}). Nel PVP compare spesso come «occupato senza titolo» o «in corso di liberazione».</p>
<h2>Affittata: quando il contratto resta</h2>
<p>Un contratto d'affitto <strong>con data certa anteriore al pignoramento</strong> vale anche per chi compra all'asta, fino alla sua scadenza ({cc('2923')}). Ci sono limiti: oltre i nove anni serve la trascrizione, e chi compra non è tenuto a rispettare un affitto con un canone inferiore di un terzo al giusto prezzo ({cc('2923')}). La perizia di solito dice se c'è un contratto e se è opponibile.</p>
<div class="avviso"><b>«Non specificato» non vuol dire libero.</b> Per molti lotti il PVP non indica lo stato di occupazione. In questo sito lo mostriamo com'è, senza indovinare: il filtro «Solo libere» usa solo il dato esplicito del PVP. La situazione vera è nella perizia e nella relazione del custode.</div>
<h2>Cosa fare prima di offrire</h2>
<ul><li>Leggi nella perizia il paragrafo sullo stato di occupazione e su eventuali contratti.</li>
<li>Prenota la visita dal PVP: il custode ti dice chi c'è in casa e a che punto è la liberazione.</li>
<li>Chiedi al delegato se l'ordine di liberazione è già stato emesso.</li></ul>"""
    if s == "rischi-casa-all-asta":
        return f"""<p class="lead">Comprare all'asta può costare meno, ma non è come comprare da un privato. Questi sono i rischi più comuni: quasi tutti si scoprono leggendo bene la perizia prima di offrire.</p>
<h2>1. Niente garanzia per i vizi</h2>
<p>Nella vendita forzata <strong>non c'è la garanzia per i vizi</strong> della cosa e la vendita non si può impugnare per lesione, cioè per la sproporzione tra prezzo e valore ({cc('2922')}). Infiltrazioni, impianti da rifare, difetti nascosti: restano a chi compra.</p>
<h2>2. Abusi edilizi e difformità</h2>
<p>La perizia segnala difformità urbanistiche e catastali e spesso stima i costi per sanarle. Alcuni abusi si possono sanare dopo l'acquisto, altri no (e vanno demoliti). È uno dei motivi principali per cui un prezzo basso può non essere conveniente: fatti spiegare dal delegato o da un tecnico cosa dice la perizia.</p>
<h2>3. Occupazione</h2>
<p>Una casa occupata può richiedere mesi prima di essere libera, e un affitto con data certa anteriore al pignoramento resta valido ({cc('2923')}). Vedi la guida <a href="{{rel}}guide/casa-occupata-all-asta/">Casa occupata all'asta</a>.</p>
<h2>4. Spese condominiali arretrate</h2>
<p>Chi compra può essere chiamato a pagare, insieme al vecchio proprietario, i contributi condominiali <strong>dell'anno in corso e di quello precedente</strong> (<a href="{NORMATTIVA_DISPATT_CC}" rel="noopener">art. 63 disp. att. c.c.</a>). Chiedi all'amministratore la situazione prima di offrire.</p>
<h2>5. Tempi e soldi</h2>
<ul><li>La cauzione (almeno il 10% dell'offerta) resta bloccata fino all'esito; se vinci e poi non paghi il saldo nel termine, perdi l'aggiudicazione e la cauzione ({cpc('587')}).</li>
<li>Il saldo va versato entro il termine dell'avviso, al massimo 120 giorni dall'aggiudicazione ({cpc('569')}): se serve un mutuo, va preparato prima.</li>
<li>Imposte e spese di trasferimento sono a tuo carico; l'avviso dice come si calcolano.</li>
<li>Il giudice può sospendere la vendita se ritiene il prezzo offerto notevolmente inferiore a quello giusto ({cpc('586')}).</li></ul>
<h2>6. Il confronto con la media di zona</h2>
<p>Lo sconto rispetto alla media OMI che vedi in questo sito è un punto di partenza, non un giudizio di convenienza: la media OMI è un intervallo indicativo per una casa «normale» della zona, mentre la tua casa può essere in condizioni molto diverse. Vedi <a href="{{rel}}guide/valori-omi/">Cosa sono i valori OMI</a>.</p>
<h2>Una lista di controllo</h2>
<ol><li>Leggi avviso di vendita e perizia per intero (nella scheda PVP).</li><li>Visita la casa con il custode (prenotazione dal PVP).</li><li>Verifica occupazione, abusi, spese condominiali.</li><li>Calcola il costo totale: prezzo, imposte, spese, lavori.</li><li>Prepara cauzione e, se serve, il mutuo.</li><li>Nel dubbio, chiedi al delegato o a un professionista di fiducia.</li></ol>"""
    if s == "mutuo-casa-all-asta":
        return f"""<p class="lead">Sì, il saldo di una casa comprata all'asta si può pagare con un mutuo. La legge lo prevede: la banca versa i soldi direttamente alla procedura e ottiene un'ipoteca di primo grado sulla stessa casa ({cpc('585')}).</p>
<h2>Come funziona</h2>
<ul><li>Il decreto di trasferimento indica il contratto di mutuo, e la vendita si trascrive insieme all'ipoteca della banca ({cpc('585')}).</li>
<li>Il saldo va pagato entro il termine dell'avviso, che non può superare i 120 giorni dall'aggiudicazione ({cpc('569')}). Se non paghi in tempo perdi l'aggiudicazione e la cauzione ({cpc('587')}).</li>
<li>Per questo conviene chiedere alla banca una valutazione <strong>prima</strong> dell'asta, con avviso e perizia in mano.</li></ul>
<h2>Dove chiedere</h2>
<p>Molti tribunali hanno accordi con le banche per finanziare chi compra all'asta: chiedi al delegato o guarda il sito del tribunale. Puoi anche rivolgerti alla tua banca o a un mediatore creditizio iscritto all'OAM.</p>
<div class="avviso"><b>La banca valuta la casa, non il prezzo dell'asta.</b> Di solito finanzia una parte del minore tra prezzo di aggiudicazione e valore di perizia. Abusi edilizi o difformità gravi possono rendere difficile ottenere il mutuo.</div>"""
    if s == "valori-omi":
        return f"""<p class="lead">L'<strong>Osservatorio del Mercato Immobiliare</strong> (OMI) dell'Agenzia delle Entrate pubblica ogni sei mesi le quotazioni delle case per ogni zona di ogni comune italiano: un valore minimo e uno massimo in euro al metro quadro, per tipologia e stato di conservazione.</p>
<h2>Cosa sono le zone OMI</h2>
<p>Ogni comune è diviso in zone omogenee (centrale, semicentrale, periferica, suburbana, rurale), con un codice come B1, C3 o D31. Le trovi sulla mappa pubblica <a href="{OMI_GEOPOI}" rel="noopener">GEOPOI</a> dell'Agenzia.</p>
<h2>Cosa misurano, e cosa no</h2>
<ul><li>Sono intervalli indicativi per immobili «ordinari» della zona, non la stima di una casa precisa. L'Agenzia stessa li presenta come un riferimento, non come un valore di perizia (<a href="{OMI_MANUALI}" rel="noopener">manuali e guide OMI</a>).</li>
<li>Di solito sono riferiti alla superficie <strong>lorda</strong>, mentre gli annunci d'asta riportano spesso la superficie commerciale o catastale: misure simili ma non identiche.</li>
<li>Escono con qualche mese di ritardo: oggi usiamo il {SEM_TESTO}.</li></ul>
<h2>Come li usiamo</h2>
<p>Con le coordinate del lotto troviamo la zona OMI in cui cade. Prendiamo la tipologia più vicina al bene (abitazione civile, economica, signorile, villa), stato «normale», e facciamo la media tra minimo e massimo. Poi dividiamo il prezzo per i metri quadri scritti nell'annuncio e confrontiamo. Se mancano i metri quadri o le coordinate, non calcoliamo nulla. Tutto in <a href="{{rel}}metodologia/">Metodo e fonti</a>.</p>
<h2>Licenza</h2>
<p>I dati OMI sono pubblicati con licenza <a href="{CC_BY}" rel="noopener license">CC BY 4.0</a> e vanno citati come «{ATTRIB}» (<a href="{OMI_FORNITURE}" rel="noopener">Forniture dati OMI</a>).</p>"""
    raise KeyError(s)


def pagine_guide():
    for s, tit, desc in GUIDE:
        altre = [g[0] for g in GUIDE if g[0] != s][:4]
        corpo = f"""<div class="pull">{DISCLAIMER_GUIDA.replace('class="avviso"', 'class="avviso" style="margin:0;box-shadow:var(--sh-2)"')}</div>
<article class="testo" style="margin-top:26px">{testo_guida(s)}</article>
{box_mutuo() if s in ('mutuo-casa-all-asta', 'come-funziona-asta-giudiziaria', 'rischi-casa-all-asta') else ''}{AD}
<h2>Altre guide</h2><ul class="guide">{voci_guide(altre)}</ul>
<h2>Le aste di oggi</h2><p class="lead">Scegli una città: <a href="{{rel}}citta/">tutte le città con case all'asta</a>.</p>"""
        testata = banda("Guida", tit, h(desc), icona="doc")
        pagina(f"guide/{s}/", f"{tit} | {NOME}", desc + " Guida in parole semplici con i riferimenti di legge.", corpo, "guida",
               briciole=[("Guide", "guide/"), (tit, f"guide/{s}/")], testata=testata,
               jsonld_extra={"@context": "https://schema.org", "@type": "Article", "headline": tit, "inLanguage": "it-IT",
                             "dateModified": OGGI.isoformat(), "author": {"@type": "Organization", "name": NOME}})
    corpo = f"""<div class="pull"><ul class="guide">{voci_guide([g[0] for g in GUIDE])}</ul></div>
<p class="lead" style="margin-top:22px">Guide brevi, con il riferimento all'articolo di legge per ogni regola. Non sostituiscono l'avviso di vendita, la perizia e il professionista delegato.</p>"""
    pagina("guide/", f"Guide alle aste giudiziarie | {NOME}", "Come funziona un'asta giudiziaria, offerta minima, casa occupata, rischi, mutuo e valori OMI: guide in parole semplici.",
           corpo, "indice", briciole=[("Guide", "guide/")], testata=banda("Guide", "Aste giudiziarie in parole semplici", "Cosa sapere prima di fare un'offerta.", icona="doc"))


# ---------------------------------------------------------------- pagine fisse
def metodologia():
    n = len(LOTTI)
    n_mq = sum(1 for L in LOTTI if L.get("mq"))
    n_omi = sum(1 for L in LOTTI if L.get("sconto_min") is not None)
    n_zona = sum(1 for L in LOTTI if L.get("zona"))
    n_parz = sum(1 for L in LOTTI if L.get("diritto") == "parziale")
    n_elenco = sum(1 for L in LOTTI if L.get("fonte") == "elenco")
    corpo = f"""<div class="testo">
<p class="lead">Questa pagina spiega da dove vengono i dati, come calcoliamo il confronto con la zona e cosa non facciamo. Edizione del {data_lunga(OGGI.isoformat())}.</p>
<h2>Le aste: Portale delle Vendite Pubbliche</h2>
<p>Leggiamo ogni giorno la ricerca pubblica del <a href="{PVP}" rel="noopener">PVP</a> (nessun accesso riservato): immobili residenziali e autoveicoli con data di vendita da oggi in poi. Per i lotti dei comuni con almeno {SOGLIA_CITTA} aste leggiamo anche la scheda pubblica del lotto, una richiesta ogni tre secondi circa e al massimo qualche centinaio al giorno: se il portale rallenta o risponde con un errore, ci fermiamo. Finché la scheda di un lotto non è stata letta ({intero(n_elenco)} lotti oggi), usiamo i campi dell'elenco: in quelle schede mancano il termine per le offerte e la modalità di vendita, e la superficie si cerca solo nel titolo breve.</p>
<p>Teniamo solo campi del lotto: prezzo base, offerta minima, rilancio minimo, data e ora della vendita, termine per le offerte, comune, strada (senza numero civico), coordinate (solo per trovare la zona OMI, non le pubblichiamo), tipologia, stato di occupazione, modalità di vendita, tribunale.</p>
<h2>Cosa scartiamo</h2>
<ul><li>Lotti con date impossibili (errori di battitura come anni oltre il 2030) o più lontane di 24 mesi.</li>
<li>Lotti senza prezzo base, offerta minima, data o comune, o con offerta minima più alta del prezzo base.</li>
<li>Lotti con un esito già registrato (sospesi, aggiudicati, deserti).</li>
<li>Lotti classificati come residenziali ma fatti solo di box, garage, cantine, negozi, uffici o terreni: li riconosciamo dal tipo di bene, dal titolo dell'annuncio e dalle categorie catastali (per esempio solo C/6, autorimessa).</li>
<li>Dalla scheda del PVP: i nomi, le email e i codici fiscali di delegati e custodi, ogni dato del debitore, gli allegati e i PDF. Non li salviamo nemmeno.</li></ul>
<h2>Superficie</h2>
<p>Il PVP non ha quasi mai la superficie in un campo apposito. La leggiamo nel testo dell'annuncio pubblicato sul PVP (un riassunto della perizia, non la perizia intera) solo quando è chiara: un solo valore riferito all'abitazione (non a giardino, box, cantina, terrazzo o terreno), oppure la «superficie commerciale/lorda/complessiva». Se i valori sono più d'uno e non coincidono, se il testo dà solo le misure dei singoli vani (soggiorno, camera, bagno…) o se il lotto contiene più abitazioni, scriviamo <strong>«superficie non indicata»</strong> e non calcoliamo il prezzo al metro quadro. Oggi abbiamo una superficie affidabile per {intero(n_mq)} lotti su {intero(n)}.</p>
<h2>Zona OMI</h2>
<p>Con le coordinate del lotto cerchiamo in quale zona OMI del comune cade il punto, usando i perimetri pubblicati dall'Agenzia delle Entrate per il {SEM_TESTO} (<a href="{OMI_GEOPOI}" rel="noopener">GEOPOI</a>). Le coordinate sono quelle inserite nel PVP e a volte sono approssimative (per esempio il centro della via): vicino al confine tra due zone il lotto può finire nella zona accanto. Se le coordinate mancano o cadono fuori dal comune, la zona resta vuota. Oggi la zona è nota per {intero(n_zona)} lotti su {intero(n)}.</p>
<h2>Il confronto</h2>
<ul><li><strong>Valore di zona</strong>: per la tipologia più vicina al bene (abitazione signorile, civile, economica o villa; per «appartamento» la tipologia prevalente della zona), stato conservativo normale, la media tra valore minimo e massimo di compravendita.</li>
<li><strong>€/m² del lotto</strong> = offerta minima ÷ metri quadri (e, a parte, prezzo base ÷ metri quadri). L'offerta minima è di solito il 75% del prezzo base ({cpc('571')}): per questo lo sconto calcolato con l'offerta minima è più ampio di quello col prezzo base.</li>
<li><strong>Sconto</strong> = €/m² con l'offerta minima ÷ media OMI − 1, arrotondato. Tra −3% e +3% scriviamo «in linea con la media OMI».</li>
<li>Non calcoliamo nulla se si vende una <strong>quota</strong> o un diritto parziale (nuda proprietà, usufrutto, diritto di superficie: {intero(n_parz)} lotti oggi), per i fabbricati in costruzione, o se il risultato è così lontano dalla zona (meno di un quarto della media, o più di tre volte la media col prezzo base) da far pensare a una superficie sbagliata: in quel caso la scheda dice «dato da verificare».</li></ul>
<p>Risultato: confronto disponibile per <strong>{intero(n_omi)} lotti su {intero(n)}</strong>.</p>
<h2>I limiti, detti chiari</h2>
<ul><li>La media OMI è un valore indicativo per una casa «normale» della zona. Una casa all'asta può essere da ristrutturare, occupata o con abusi: lo sconto può essere giustificato.</li>
<li>Le quotazioni OMI si riferiscono di solito alla superficie lorda; gli annunci spesso a quella commerciale o catastale.</li>
<li>Quando nello stesso lotto ci sono un box o una cantina, il loro prezzo è compreso: il €/m² dell'abitazione risulta un po' più alto (lo sconto è prudente).</li>
<li>Il PVP non dice in modo affidabile a quale tentativo d'asta siamo: lo trovi nell'avviso di vendita.</li></ul>
<h2>Aggiornamenti</h2>
<p>Ogni giorno rileggiamo prezzi, date ed esiti e scriviamo un piccolo file di dati che le pagine leggono quando le apri: i numeri si aggiornano e le aste già svolte o tolte dal PVP spariscono, anche se la pagina è stata pubblicata giorni prima. Le pagine (nuove aste, nuove città) si rigenerano una volta a settimana. Le quotazioni OMI cambiano a ogni semestre.</p>
<h2>Parole che non usiamo</h2>
<p>Non diciamo mai che un lotto è un «affare» o un'«occasione»: scriviamo i fatti (prezzo, metri quadri, media di zona, occupazione) e il link alla scheda ufficiale. Nessun consiglio d'acquisto personalizzato.</p>
<h2>Licenze e citazioni</h2>
<p>Valori OMI: «{ATTRIB}», licenza <a href="{CC_BY}" rel="noopener license">CC BY 4.0</a> (<a href="{OMI_FORNITURE}" rel="noopener">Forniture dati OMI</a>); li abbiamo elaborati (media, confronto) e l'Agenzia non ha controllato né approvato questo sito. Dati delle aste: Portale delle Vendite Pubbliche, Ministero della Giustizia, solo campi pubblici e link alla scheda.</p>
</div>"""
    testata = banda("Metodo", "Metodo e fonti", "Da dove vengono i numeri, come calcoliamo lo sconto sulla zona e cosa scartiamo.", icona="db")
    pagina("metodologia/", f"Metodo e fonti | {NOME}", "Come leggiamo le aste del Portale delle Vendite Pubbliche, come troviamo la zona OMI e calcoliamo il confronto €/m², cosa scartiamo.",
           corpo, "fissa", briciole=[("Metodo", "metodologia/")], testata=testata)


def chi_siamo():
    corpo = f"""<div class="testo">
<p class="lead">{NOME} risponde a una domanda con dati pubblici: <em>questa casa all'asta costa più o meno delle altre case della zona?</em></p>
<p>Le aste giudiziarie sono pubbliche, ma i numeri sono sparsi tra il Portale delle Vendite Pubbliche, gli avvisi e le perizie, e confrontarli con i prezzi della zona richiede tempo. Noi mettiamo in fila, per ogni città, prezzo base, offerta minima, data, occupazione e il confronto con le quotazioni OMI dell'Agenzia delle Entrate.</p>
<h2>Le nostre regole</h2>
<ul><li>Solo dati pubblici, con la fonte e la data su ogni pagina e il link alla scheda ufficiale di ogni lotto.</li>
<li>Nessun dato personale: niente nomi di debitori, delegati o custodi, niente documenti delle procedure.</li>
<li>Nessuna promessa: mostriamo i numeri e i loro limiti, senza giudizi di convenienza.</li>
<li>Nessuna consulenza: per un'offerta servono l'avviso, la perizia e il professionista delegato.</li></ul>
<h2>Chi c'è dietro</h2>
<p>{NOME} è un progetto indipendente di Massimiliano Cori. Non è collegato al Ministero della Giustizia, ai tribunali, ai gestori delle vendite o all'Agenzia delle Entrate. Il sito può mostrare pubblicità e, in futuro, un riquadro chiaramente segnalato per confrontare mutui: non cambiano mai i dati.</p>
<h2>Errori e richieste</h2>
<p>Hai trovato un dato sbagliato o un'informazione che non dovrebbe esserci? <a href="{{rel}}contatti/?ref=chi-siamo">Scrivici</a>: controlliamo e correggiamo al prossimo aggiornamento, o subito se si tratta di dati personali.</p></div>"""
    testata = banda("Chi siamo", f"Chi siamo", "Un sito indipendente che mette accanto le aste di case e i valori di zona, con dati pubblici.", icona="info")
    pagina("chi-siamo/", f"Chi siamo | {NOME}", f"{NOME}: sito indipendente che confronta le case all'asta del PVP con i valori OMI di zona.",
           corpo, "fissa", briciole=[("Chi siamo", "chi-siamo/")], testata=testata)


def contatti():
    corpo = f"""<section class="card pull"><form class="form ajax" name="contatti" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contatti"><input type="hidden" name="source" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>La tua email<input type="email" name="email" required autocomplete="email"></label>
<label>Pagina o numero del lotto (facoltativo)<input type="text" name="pagina" maxlength="200"></label>
<label>Messaggio<textarea name="messaggio" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>Ho letto l'<a href="{{rel}}privacy.html">informativa sulla privacy</a>.</span></label>
<button class="btn" type="submit">Invia</button><p class="errore" data-errore hidden>Non è andata a buon fine. Riprova tra poco.</p></form>
<div class="ok" data-ok hidden><strong>Grazie.</strong> Controlliamo e ti rispondiamo per email.</div></section>
<p class="small" style="margin-top:16px">Non possiamo dare consigli su singole aste né metterti in contatto con delegati o custodi: i loro contatti sono nella scheda del lotto sul PVP.</p>"""
    testata = banda("Contatti", "Scrivici", "Per segnalare un errore nei dati o chiedere di togliere un'informazione.", icona="doc")
    pagina("contatti/", f"Contatti | {NOME}", f"Scrivi a {NOME} per segnalare un errore nei dati.", corpo, "fissa",
           briciole=[("Contatti", "contatti/")], testata=testata)


def privacy():
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("it", SITO_ID, ci_sono_affiliati()) or """<h2>Cookie e contatore visite</h2><p>Il sito non usa cookie di profilazione. Per contare le visite usiamo <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, un contatore rispettoso della privacy: non usa cookie e non salva nulla nel browser, non crea profili e non conserva l'indirizzo IP, la firma completa del browser né altri identificativi. Tiene solo numeri aggregati (pagina, ora o giorno, browser, Paese, larghezza dello schermo) su server nell'Unione europea e non cede nulla a terzi; vedi l'<a href="https://www.goatcounter.com/help/privacy" rel="noopener">informativa privacy di GoatCounter</a>. Se aggiungeremo pubblicità o link sponsorizzati, aggiorneremo questa informativa e chiederemo il consenso dove serve, prima di qualsiasi cookie pubblicitario.</p>"""
    corpo = f"""<div class="testo"><p class="small">Ultimo aggiornamento: {MESI[OGGI.month - 1]} {OGGI.year}</p>
<h2>Chi è il titolare</h2><p>Il titolare del trattamento è Massimiliano Cori (Italia), che gestisce {NOME} come progetto indipendente. Contatto: il <a href="{{rel}}contatti/">modulo contatti</a>.</p>
<h2>I dati delle aste</h2><p>Pubblichiamo solo campi del lotto letti dal Portale delle Vendite Pubbliche: prezzi, date, comune, strada senza numero civico, tipologia, stato di occupazione, tribunale. <strong>Non pubblichiamo e non salviamo</strong> nomi, email, telefoni o codici fiscali di delegati, custodi e giudici, dati del debitore, documenti o allegati delle procedure. Per i veicoli non pubblichiamo la targa né la descrizione dell'annuncio. Se pensi che una pagina contenga un dato personale, scrivici: lo togliamo subito.</p>
<h2>Cosa raccogliamo su di te</h2><p>Solo quello che scrivi nel modulo contatti (email, pagina, messaggio) e la pagina da cui arrivi. Se scegli il tema chiaro o scuro, la scelta resta nel tuo browser.</p>
<h2>Il file dei prezzi aggiornati</h2><p>Per mostrarti prezzi e date del giorno, le pagine con le aste scaricano un piccolo file di dati da GitHub (raw.githubusercontent.com, servizio di GitHub, Inc.). Come per ogni richiesta web, GitHub riceve il tuo indirizzo IP e i dati tecnici del browser; il file non contiene dati personali e non usiamo cookie per questo.</p>
<h2>Perché</h2><p>Per rispondere ai messaggi e correggere il sito. La base giuridica è il tuo consenso (art. 6, par. 1, lett. a GDPR), che puoi revocare quando vuoi.</p>
<h2>Chi tratta i dati per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i messaggi per nostro conto e può trattarli fuori dall'Unione europea con le garanzie previste dal GDPR (clausole contrattuali standard). Netlify tiene registri tecnici del server (come gli indirizzi IP) per sicurezza. Non vendiamo e non cediamo i tuoi dati.</p>
{cookie}
<h2>Per quanto tempo</h2><p>I messaggi restano al massimo 12 mesi dall'ultimo scambio.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, rettifica, cancellazione, limitazione, portabilità e opposizione (artt. 15–22 GDPR) e puoi rivolgerti al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p></div>"""
    testata = banda("Privacy", "Informativa sulla privacy", "Cosa raccogliamo (pochissimo) e cosa non pubblichiamo mai.", icona="shield")
    pagina("privacy.html", f"Privacy | {NOME}", f"Informativa sulla privacy di {NOME}.", corpo, "fissa", testata=testata)


# ---------------------------------------------------------------- file accessori
def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in aste/sito (ogni pubblicazione consuma crediti Netlify).
  # I dati giornalieri stanno in aste/dati/ (fuori da questa cartella): i loro commit non fanno ripartire Netlify.
  # Impostazioni del sito su Netlify: Base directory = aste/sito, Build command vuoto, Publish directory = aste/sito (cioè ".").
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
""")
    grandi = citta_ordinate()[:12]
    corpo = f"""<div class="pull card"><p style="margin:0 0 10px">La pagina potrebbe essere stata tolta dopo un aggiornamento (per esempio una zona o una fascia di prezzo con troppe poche aste).</p>
<ul class="chips">{''.join(f'<li><a href="/{url_citta(k)}">{h(k[0])}</a></li>' for k in grandi)}<li><a href="/citta/">Tutte le città</a></li></ul></div>"""
    pagina("404.html", f"Pagina non trovata | {NOME}", "Pagina non trovata.", corpo, "404", indicizza=False, assoluto=True,
           testata=banda("Errore 404", "Pagina non trovata", "Scegli una città o torna alla home.", icona="alert"))


def copia_grafica():
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").iterdir():
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")


def controlli():
    err = []
    for L in LOTTI:
        if not (L.get("base") and L.get("minima") and L.get("data") and L.get("comune")):
            err.append(f"lotto {L.get('id')}: campi mancanti")
        if int(L["data"][:4]) > 2030:
            err.append(f"lotto {L['id']}: data implausibile {L['data']}")
        if L.get("sconto_min") is not None and not (L.get("mq") and L.get("omi")):
            err.append(f"lotto {L['id']}: sconto senza superficie o OMI")
    if len(set(SLUG_CITTA.values())) != len(SLUG_CITTA):
        err.append("slug di città duplicati")
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
    pagina_indice_citta()
    for k in sorted(CITTA, key=lambda k: norm(k[0])):
        pagina_citta(k)
    pagina_auto()
    pagine_guide()
    metodologia()
    chi_siamo()
    contatti()
    privacy()
    extra()
    con = sum(1 for L in LOTTI if L.get("sconto_min") is not None)
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili {CONTI}. Lotti: {len(LOTTI)} in {len(CITTA)} città, "
          f"{con} con confronto €/m²; veicoli {len(VEICOLI)}; OMI {SEM_TESTO}; PVP letto il {LETTO}"
          + (f"; {SCADUTI_ALLA_GENERAZIONE} lotti già passati esclusi" if SCADUTI_ALLA_GENERAZIONE else "") + ".")


if __name__ == "__main__":
    main()
