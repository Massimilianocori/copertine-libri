"""Genera il sito statico "Statute of Limitations by State" (inglese, USA) in limits/sito/.

Uso (dalla radice del repository):
    python3 limits/raccolta/fonti.py     # scarica i testi di legge ufficiali (raccolta/_grezzi/, fuori da git) -> dati/fonti.json
    python3 limits/genera.py             # pagine in limits/sito/
    python3 limits/verifica.py           # controlli (rilegge ogni termine dal testo di legge; --browser per Playwright)

Contenuto: 10 Stati (TX, FL, OH, WA, VA, NC, MI, AZ, MA, MN) × 6 cause civili = 59 pagine (manca Washington × wrongful death:
nessun termine scritto nella legge), 10 pagine di Stato, 6 pagine di causa con il confronto, calcolatore della scadenza generale.
Ogni termine ha il testo di legge citato tra virgolette, con link ufficiale e data di lettura (norme.py, controllato qui contro il
file salvato). Regole legali: informazione e non consulenza (frase fissa su ogni pagina), nessun modulo, nessuna intermediazione di
debiti, nessuna pagina sugli abusi su minori. Nessun dato personale.
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import date, timedelta
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import norme as N  # noqa: E402
import stile  # noqa: E402
import testo as T  # noqa: E402

URL_SITO = "https://statute-limits-by-state.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
NOME = "Statute of Limitations by State"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "limits"  # nome del sito in monetizzazione.json

FONTI = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))
FAQ = json.loads((DATI / "faq.json").read_text(encoding="utf-8"))["faq"]
AFF = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8"))
LETTO = date.fromisoformat(N.VERIFICATO_IL)
STATI, CELLE, CAUSE = N.STATI, N.CELLE, N.CAUSE
OS, OC = N.ORDINE_STATI, N.ORDINE_CAUSE
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
NUMERI = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d[:10])
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def anni(n, parole=False):
    if parole:
        return f"{NUMERI.get(n, n)} year{'s' if n != 1 else ''}"
    return f"{n} year{'s' if n != 1 else ''}"


def cap(s):
    return s[:1].upper() + s[1:]


# ---------------------------------------------------------------- calcolo (Python; verifica.py ne ha uno suo, scritto a parte)
def piu_anni(d, n):
    y = d.year + n
    if d.month == 2 and d.day == 29 and not (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)):
        return date(y, 2, 28)
    return d.replace(year=y)


def calcola(chiave, d):
    c = CELLE[chiave]
    out = []
    for v in c["varianti"]:
        tr = v.get("transizione")
        inizio = d + timedelta(days=v.get("giorni_dopo", 0))  # la regola transitoria guarda il giorno in cui il diritto sorge
        if tr and inizio < date.fromisoformat(tr["data"]):
            out.append((v["etichetta"], None, v["cit"]))
            continue
        a, et, cit = v["anni"], v["etichetta"], v["cit"]
        p = v.get("prima")
        if p and d <= date.fromisoformat(p["fino_al"]):
            a, et, cit = p["anni"], p["etichetta"], p["cit"]
        out.append((et, piu_anni(inizio, a), cit))
    rip = piu_anni(d, c["repose"]["anni"]) if c.get("repose") else None
    return out, rip


# ---------------------------------------------------------------- controlli sui dati prima di generare
def controlli():
    err = []
    for fid, v in FONTI.items():
        if v.get("http") != 200 or not v.get("sha256"):
            err.append(f"fonte {fid}: ultima lettura non riuscita")
            continue
        f = T.GREZZI / v["file"]
        if not f.exists():
            err.append(f"fonte {fid}: manca {f} (lanciare raccolta/fonti.py)")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != v["sha256"]:
            err.append(f"fonte {fid}: impronta diversa da dati/fonti.json")

    def cerca(dove, fid, frammenti):
        if fid not in FONTI:
            err.append(f"{dove}: fonte sconosciuta {fid}")
            return
        for fr in frammenti:
            if not T.contiene(fid, fr):
                err.append(f"{dove}: citazione non trovata in {fid}: «{fr[:80]}»")

    for k, s in STATI.items():
        for e in s["regole"] + s["governo"]:
            cerca(f"{k} {e['titolo']}", e["fonte"], e["testo"])
        for c in s["cambi"]:
            cerca(f"{k} cambio", c["fonte"], c["testo"] if isinstance(c["testo"], list) else [c["testo"]])
    for k, c in CELLE.items():
        for v in c["varianti"] + ([c["repose"]] if c.get("repose") else []):
            cerca(f"{k} {v['etichetta']}", v["fonte"], v["testo"])
            if not any(v["frase"] in t for t in v["testo"]):
                err.append(f"{k}: la frase del termine non è nella citazione")
            if v.get("prima"):
                cerca(f"{k} prima", v["prima"]["fonte"], v["prima"]["testo"])
        for e in c["eccezioni"]:
            cerca(f"{k} {e['titolo']}", e["fonte"], e["testo"])
        if c.get("inizio_testo"):
            cerca(f"{k} inizio", c["inizio_testo"]["fonte"], c["inizio_testo"]["testo"])
    if len(CELLE) != 59:
        err.append(f"celle attese 59, trovate {len(CELLE)}")
    if date.today() > LETTO + timedelta(days=400):
        err.append("testi di legge letti più di 13 mesi fa: rileggerli (NOTE.md, aggiornamento annuale)")
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err))


# ---------------------------------------------------------------- risorse
def _impronta(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:10]


CSS = re.sub(r"\n", "", stile.CSS)
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in stile.ICONE.items()) + "</svg>\n")
ICONS_FILE = f"icons.{_impronta(SPRITE)}.svg"
APP_JS = stile.CALC_JS.strip() + "\n" + stile.APP_JS.strip() + "\n"
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


# ---------------------------------------------------------------- fonti e rimandi
class Rimandi:
    def __init__(self):
        self.ordine = []

    def n(self, fid):
        if fid not in FONTI:
            raise SystemExit(f"fonte sconosciuta: {fid}")
        if fid not in self.ordine:
            self.ordine.append(fid)
        return self.ordine.index(fid) + 1

    def ref(self, fid):
        k = self.n(fid)
        return f'<sup class="ref"><a href="#f{k}" aria-label="source {k}">[{k}]</a></sup>'

    def elenco(self):
        if not self.ordine:
            return ""
        voci = []
        for k, fid in enumerate(self.ordine, 1):
            f = FONTI[fid]
            voci.append(f'<li id="f{k}"><a href="{h(f["link"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. '
                        f'<span class="small">Official text read on {data_lunga(f["letto_il"])}; saved copy fingerprint (SHA-256) '
                        f'{f["sha256"][:12]}….</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2>'
                f'<ol>{"".join(voci)}</ol><p class="small">We quote the statute text as published by each legislature and re-check every '
                f'quotation and period against a saved copy before each update; see <a href="/how-we-check/">how we check</a>.</p></section>')


def citazione(rim, fid, frammenti, cit, extra=""):
    """Blocco con il testo di legge tra virgolette e la riga di citazione con link ufficiale e data di lettura."""
    f = FONTI[fid]
    righe = "".join(f"<p>{h(T.normalizza(x))}</p>" for x in frammenti)
    return (f'<blockquote class="legge" data-fonte="{fid}">{righe}</blockquote>'
            f'<p class="cita">{h(cit)} · <a href="{h(f["link"])}" rel="noopener">official text</a> ({h(f["chi"])}), read on '
            f'{data_lunga(f["letto_il"])}{rim.ref(fid)}{extra}</p>')


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
TITOLI = {}
DESCR = {}
MENU = [("#calculator", "Calculator"), ("personal-injury/", "Personal injury"), ("debt/", "Debt"), ("breach-of-contract/", "Contracts"),
        ("how-we-check/", "How we check")]
DISCLAIMER = ("<strong>General information, not legal advice, and not a substitute for the advice of an attorney.</strong> The deadline in a "
              "real case can be shorter or longer than the general period shown here: exceptions, notice rules and court decisions can change it, "
              "and court rules decide when a case counts as filed. Talk to a licensed attorney in your state. This site is independent: it is not "
              "a law firm or a government website, and using it does not create an attorney-client relationship.")
AVVISO = ('<div class="avviso">' + "{ico}" + '<p><strong>Estimate, not legal advice.</strong> Deadlines can be shorter or longer than the general '
          'period. Talk to a licensed attorney in {dove}.</p></div>')


def avviso(dove="your state"):
    return AVVISO.replace("{ico}", ico("alert")).replace("{dove}", h(dove))


def menu_html(percorso):
    voci = []
    for u, t in MENU:
        href = "/" + u if not u.startswith("#") else "/" + u
        voci.append(f'<a href="{href}"' + (' aria-current="page"' if u == percorso else "") + f">{h(t)}</a>")
    return "".join(voci)


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, pubblicita=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
    url_pag = f"{URL_SITO}/{percorso}"
    if len(titolo) > 65 or not 70 <= len(descrizione) <= 160:
        raise SystemExit(f"titolo o descrizione fuori misura ({len(titolo)}, {len(descrizione)}): {percorso}")
    if titolo in TITOLI or descrizione in DESCR:
        raise SystemExit(f"titolo o descrizione doppia: {percorso}")
    TITOLI[titolo], DESCR[descrizione] = percorso, percorso
    if indicizza:
        URLS.append(percorso)
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": i, "name": nn, "item": f"{URL_SITO}/{p}"} for i, (nn, p) in enumerate(briciole, 1)]
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb">' + " › ".join(
            [f'<a href="/{p}">{h(nn)}</a>' for nn, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    stati_piede = "".join(f'<li><a href="/{STATI[s]["slug"]}/">{h(STATI[s]["nome"])}</a></li>' for s in OS)
    cause_piede = "".join(f'<li><a href="/{c}/">{h(CAUSE[c]["nome"])}</a></li>' for c in OC)
    testa_ads = MON.script_adsense(SITO_ID, con_pubblicita=indicizza and pubblicita)
    testo_pag = f"""<!DOCTYPE html>
<html lang="en-US">
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
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#16213A">
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
<a class="logo" href="/">{LOGO}<span>Statute of Limitations <b>by State</b></span></a>
<nav class="menu" aria-label="Main">{menu_html(percorso)}</nav>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Menu">{ico("menu")}</summary><nav aria-label="Main">{menu_html(percorso)}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo}
<p class="disclaimer">{DISCLAIMER}</p>
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="/">{LOGO}<span>Statute of Limitations <b>by State</b></span></a>
<p><strong>{NOME}</strong> shows the general deadlines to file common civil lawsuits in ten states, with the text of each statute,
a link to the legislature's official site and the date we read it. Statutes read on {data_lunga(LETTO)}.</p>
<p>Not legal advice and not a substitute for the advice of an attorney. <a href="/about/">About</a> · <a href="/how-we-check/">How we check</a> · <a href="/privacy/">Privacy</a></p>
</div><div>
<h2>States</h2><ul>{stati_piede}</ul>
</div><div>
<h2>Claims</h2><ul>{cause_piede}</ul>
</div></div>
<p class="f-base">Statute text is quoted from the official websites of each state legislature and from the eCFR; one Washington court ruling is quoted from the state courts' website. This site is not affiliated with
any court, legislature, government agency or law firm.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo_pag, encoding="utf-8")


def banda(eyebrow, titolo, sub, corta=False, icona="scale"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>
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


# ---------------------------------------------------------------- testi brevi sui termini
def periodi(chiave):
    """Anni delle varianti (senza doppioni, nell'ordine), es. [5, 4]."""
    out = []
    for v in CELLE[chiave]["varianti"]:
        if v["anni"] not in out:
            out.append(v["anni"])
    return out


def periodi_breve(chiave):
    p = periodi(chiave)
    if len(p) == 1:
        return anni(p[0])
    return ", ".join(str(x) for x in p[:-1]) + f" or {anni(p[-1])}"


def url_cella(chiave):
    s, c = chiave.split("/")
    return f"/{STATI[s]['slug']}/{c}/"


def cella_vs(v, chiave, i, sotto=""):
    return f'<span data-v="{chiave}/{i}{sotto}">{anni(v["anni"])}</span>'


# ---------------------------------------------------------------- dati del calcolatore (JSON nella pagina)
def dati_calcolatore():
    celle = {}
    for k, c in CELLE.items():
        s, ca = k.split("/")
        vs = []
        for v in c["varianti"]:
            d = {"l": v["etichetta"], "a": v["anni"], "cit": v["cit"]}
            if v.get("giorni_dopo"):
                d["g"] = v["giorni_dopo"]
            if v.get("nota_data"):
                d["nd"] = v["nota_data"]
            if v.get("prima"):
                p = v["prima"]
                d["prima"] = {"fino": p["fino_al"], "a": p["anni"], "l": p["etichetta"], "cit": p["cit"]}
            if v.get("transizione"):
                d["tr"] = {"data": v["transizione"]["data"], "msg": v["transizione"]["messaggio"]}
            vs.append(d)
        r = c.get("repose")
        ecc = [e["titolo"] + " (" + e["cit"] + ")" for e in c["eccezioni"] if e is not N.REG_F]
        if not c.get("senza_regole_stato"):
            ecc += [e["titolo"] + " (" + e["cit"] + ")" for e in STATI[s]["regole"]]
        rip = None
        if r:
            rip = {"l": r["etichetta"], "a": r["anni"], "cit": r["cit"]}
            if r.get("nota_data"):
                rip["nd"] = r["nota_data"]
        celle[k] = {"n": f"{STATI[s]['nome']}, {CAUSE[ca]['breve']}", "v": vs, "u": url_cella(k), "e": ecc[:6], "r": rip}
        if c.get("data_etichetta"):
            celle[k]["d"] = c["data_etichetta"]
        if ca in CAUSE_ILLECITO:  # i preavvisi agli enti pubblici letti riguardano le cause per danni (tort), non i contratti
            celle[k]["gv"] = [e["titolo"] + " (" + e["cit"] + ")" for e in STATI[s]["governo"]]
    return {"celle": celle, "date": {c: CAUSE[c]["data"] for c in OC}}


CAUSE_ILLECITO = ("personal-injury", "medical-malpractice", "wrongful-death", "property-damage")
DATI_CALC = dati_calcolatore()
# Il calcolatore completo (home, Stati, cause) legge tutti i dati da UN file in cache; le pagine di una cella portano solo la loro cella.
DATI_JS = "window.SOL_DATI=" + json.dumps(DATI_CALC, ensure_ascii=False, separators=(",", ":")) + ";\n"
DATI_FILE = f"calc.{_impronta(DATI_JS)}.js"
LIMITI_CALC = ("The result is only the general period counted from the date you enter: no pause (tolling), discovery rule, exception or notice "
               "deadline is applied, and the date is not moved when it falls on a weekend or a court holiday.")


def calcolatore(stato=None, causa=None):
    """Calcolatore: completo (Stato, causa, data) o di una sola cella (solo data)."""
    if stato and causa:
        k = f"{stato}/{causa}"
        sola = {"celle": {k: DATI_CALC["celle"][k]}, "date": {causa: CAUSE[causa]["data"]}}
        json_dati = json.dumps(sola, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        script = f'<script type="application/json" id="dati-calc">{json_dati}</script>'
        return (f'<div class="card calc uno" data-calc data-stato="{stato}" data-causa="{causa}">'
                f'<form><label><span data-etichetta>{h(CELLE[k].get("data_etichetta", CAUSE[causa]["data"]))}</span><input type="date" name="data" required min="1950-01-01" max="2100-12-31"></label>'
                f'<button class="btn" type="submit">{ico("calendar")}Show the deadline</button></form>'
                f'<div class="esito" hidden aria-live="polite"></div>'
                f'<p class="small limiti-calc" style="margin:0">{h(LIMITI_CALC)} Dates you type stay in your browser.</p></div>{script}')
    script = f'<script src="/assets/{DATI_FILE}" defer></script>'
    o_stati = "".join(f'<option value="{s}"{" selected" if s == stato else ""}>{h(STATI[s]["nome"])}</option>' for s in OS)
    o_cause = "".join(f'<option value="{c}">{h(CAUSE[c]["nome"])}</option>' for c in OC)
    return (f'<div class="card calc" data-calc id="calculator"><form>'
            f'<label>State<select name="stato">{o_stati}</select></label>'
            f'<label>Type of claim<select name="causa">{o_cause}</select></label>'
            f'<label><span data-etichetta>{h(CAUSE[OC[0]]["data"])}</span><input type="date" name="data" required min="1950-01-01" max="2100-12-31"></label>'
            f'<button class="btn" type="submit">{ico("calendar")}Calculate</button>'
            f'<p class="small" data-manca hidden style="grid-column:1/-1;margin:0">Not published for this state: the statute does not state its own deadline.</p></form>'
            f'<div class="esito" hidden aria-live="polite"></div>'
            f'<p class="small limiti-calc" style="margin:0">Estimate, not legal advice. {h(LIMITI_CALC)} Deadlines can be shorter or longer: '
            f'talk to a licensed attorney in your state. Dates you type stay in your browser.</p></div>{script}')


# ---------------------------------------------------------------- FAQ
def riempi(t):
    def sost(m):
        tipo, k, i = m.group(1), m.group(2), int(m.group(3))
        v = CELLE[k]["varianti"][i]
        if tipo == "P":
            return anni(v["anni"], parole=True)
        if tipo == "CIT":
            return v["cit"]
        raise SystemExit(f"segnaposto sconosciuto {m.group(0)}")
    return re.sub(r"\{(P|CIT):([A-Z]{2}/[a-z-]+):(\d)\}", sost, t)


def faq_blocco(pid, rim, titolo="Common questions"):
    voci = [x for x in FAQ if x["pagina"] == pid]
    if not voci:
        return "", None
    blocchi, ld = [], []
    for x in voci:
        a = cap(riempi(x["a"]))
        refs = "".join(rim.ref(f) for f in x["fonti"])
        blocchi.append(f'<div class="faq"><h3>{h(x["q"])}</h3><p>{h(a)}{refs}</p></div>')
        ld.append({"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": a}})
    html_ = (f'<h2 id="faq">{h(titolo)}</h2><p class="small">Questions people in the United States search for, answered from the statute text. '
             f'General information, not legal advice.</p>' + "".join(blocchi))
    return html_, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


# ---------------------------------------------------------------- riquadro affiliati (preparato, spento)
def box_affiliati(contesto, aff=None):
    """Riquadro per i servizi di documenti legali: '' finché nessun programma è attivo con un URL vero (FlexOffers non ancora iscritto)."""
    aff = aff if aff is not None else AFF
    voci = [v for k, v in aff.items() if not k.startswith("_") and v.get("attivo") and (v.get("url") or "").startswith("https://")
            and contesto in v.get("pagine", [])]
    if not voci:
        return "<!-- partner box: off -->"
    righe = "".join(f'<li><a href="{h(v["url"])}" rel="sponsored noopener">{h(v["nome"])}</a>: {h(v["testo"])}</li>' for v in voci)
    return (f'<aside class="nota info">{ico("doc")}<p><strong>Legal documents online</strong> (partner links). These services sell document '
            f'templates; they are not law firms and do not change any deadline on this page.</p><ul>{righe}</ul>{MON.nota_trasparenza("en")}</aside>')


# ---------------------------------------------------------------- pezzi comuni
def nota_debito():
    """Pagine sui debiti: scaduto il termine per fare causa non vuol dire debito cancellato (le leggi citate non lo dicono)."""
    return (f'<div class="nota info" data-nota-debito>{ico("info")}<p><strong>A deadline to sue is not the end of the debt.</strong> The statutes quoted on this '
            f'page limit when a lawsuit can be brought; they do not say that the debt is cancelled or erased once the period has run. The federal '
            f'rule quoted on this page (Regulation F) applies to a “debt collector” as that regulation defines the term (12 CFR 1006.2(i)), so it does '
            f'not cover every creditor. What appears on a credit report follows a different federal law that this site does not cover. Whether a '
            f'payment or a written acknowledgment changes the deadline depends on state law; this site mentions it only where a quoted statute says so.</p></div>')


def blocco_eccezione(rim, e):
    return f'<div class="ecc"><h3>{h(e["titolo"])}</h3><p>{h(e["spiega"])}</p>{citazione(rim, e["fonte"], e["testo"], e["cit"])}</div>'


def blocco_cambio(rim, c):
    testo_ = c["testo"] if isinstance(c["testo"], list) else [c["testo"]]
    return (f'<div class="ecc"><h3>{h(c["titolo"])}</h3><p class="small">{ico("history")} Effective {data_lunga(c["data"])}</p>'
            f'<p>{h(c["spiega"])}</p>{citazione(rim, c["fonte"], testo_, c["cit"])}</div>')


def tabella_confronto(causa, attuale=None):
    righe = []
    for s in OS:
        k = f"{s}/{causa}"
        st = STATI[s]
        if k not in CELLE:
            righe.append(f'<tr><td><a href="/{st["slug"]}/">{h(st["nome"])}</a></td><td class="n">not published</td><td colspan="2">'
                         f'{h(st.get("assente", {}).get(causa, ""))}</td></tr>')
            continue
        c = CELLE[k]
        per = "<br>".join(f'{cella_vs(v, k, i)} <small>{h(v["etichetta"])}</small>' for i, v in enumerate(c["varianti"]))
        cit = "<br>".join(h(v["cit"]) for v in c["varianti"])
        rip = anni(c["repose"]["anni"]) if c.get("repose") else "–"
        righe.append(f'<tr{' class="qui"' if s == attuale else ""}><td><a href="{url_cella(k)}">{h(st["nome"])}</a></td>'
                     f'<td class="n">{per}</td><td>{cit}</td><td class="n">{rip}</td></tr>')
    return (f'<div class="tab"><table class="dati"><thead><tr><th>State</th><th>General period</th><th>Statute</th><th>Outer limit</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody><caption>General periods from the statute text read on {data_lunga(LETTO)}. “Outer limit” is a '
            f'statute of repose or similar cap, where the statute sets one.</caption></table></div>')


def esempio(chiave):
    d0 = date(2025, 1, 15)
    ris, rip = calcola(chiave, d0)
    parti = [f"{et}: {data_lunga(sc)}" for et, sc, _ in ris if sc]
    testo_ = f"For example, counted from {data_lunga(d0)}, the general deadline would be " + "; ".join(parti)
    if rip:
        testo_ += f", with the outer limit on {data_lunga(rip)}"
    return testo_ + ". Exceptions below can move it."


# ---------------------------------------------------------------- pagina Stato × causa
def pagina_cella(k):
    s, ca = k.split("/")
    st, cc, c = STATI[s], CAUSE[ca], CELLE[k]
    rim = Rimandi()
    vs = c["varianti"]
    breve = periodi_breve(k)
    prima_cit = vs[0]["cit"]
    sub = (f"Generally <strong>{h(breve)}</strong> under {h(prima_cit)}" + (" and related sections" if len({v['cit'] for v in vs}) > 1 else "") +
           f". Statute text, when the clock starts, exceptions and a deadline calculator. Read on {data_lunga(LETTO)}.")
    testata = banda(f"{st['nome']} · {cc['nome']}", f"{st['nome']} statute of limitations for {cc['breve']}", sub)
    celle_cifre = []
    for i, v in enumerate(vs[:3]):
        celle_cifre.append(f'<div class="cifra{" main" if i == 0 else ""}"><b>{cella_vs(v, k, i)}</b><span>{h(v["etichetta"])} · {h(v["cit"])}</span></div>')
    if len(celle_cifre) < 3 and c.get("repose"):
        r = c["repose"]
        celle_cifre.append(f'<div class="cifra"><b><span data-v="{k}/r">{anni(r["anni"])}</span></b><span>Outer limit · {h(r["cit"])}</span></div>')
    if len(celle_cifre) < 3:
        celle_cifre.append(f'<div class="cifra"><b>{len(c["eccezioni"]) + (0 if c.get("senza_regole_stato") else len(st["regole"]))}</b>'
                           f'<span>exceptions and tolling rules quoted on this page</span></div>')
    corpo = (f'<div class="card cifre pull">{"".join(celle_cifre)}<p class="asof">{ico("check")}Statute text read on the official '
             f'{h(st["nome"])} legislature website on {data_lunga(LETTO)}.</p></div>')
    corpo += avviso(f"{st['nome']}")
    # testo di legge
    corpo += f'<h2 id="statute">What the {h(st["nome"])} statute says</h2>'
    if len(vs) > 1:
        corpo += f'<p>{h(st["nome"])} sets more than one period for {h(cc["breve"])} claims, depending on the kind of claim:</p>'
    corpo += '<ul class="var">'
    for i, v in enumerate(vs):
        extra = ""
        if v.get("nota_data"):
            extra = f'<p class="small">{h(v["nota_data"])}</p>'
        if v.get("prima"):
            p = v["prima"]
            extra += (f'<p><strong>{h(p["etichetta"])}:</strong> <span data-v="{k}/{i}/prima">{anni(p["anni"])}</span> under the law before '
                      f'March 24, 2023.</p>' + citazione(rim, p["fonte"], p["testo"], p["cit"]))
        corpo += (f'<li><h3>{h(v["etichetta"])} <span class="periodo">{cella_vs(v, k, i)}</span></h3>'
                  f'{citazione(rim, v["fonte"], v["testo"], v["cit"])}{extra}</li>')
    corpo += "</ul>"
    if any(v.get("transizione") for v in vs):
        corpo += (f'<div class="nota">{ico("history")}<p>For claims that accrued before {data_lunga(vs[0]["transizione"]["data"])}, a transition rule in '
                  f'Senate Bill 13 (134th General Assembly) applies: the deadline is the earlier of the new period counted from that date or the end of '
                  f'the period that applied before. The rule is quoted under <a href="#changes">recent changes</a>. The calculator shows no date for '
                  f'those claims; ask an Ohio attorney.</p></div>')
    if ca == "debt":
        corpo += nota_debito()
    if c.get("nota"):
        corpo += f'<div class="nota info">{ico("info")}<p>{h(c["nota"])}</p></div>'
    # decorrenza
    corpo += f'<h2 id="start">When the clock starts</h2><div class="testo"><p>{h(c["inizio"])}</p></div>'
    if c.get("inizio_testo"):
        it = c["inizio_testo"]
        corpo += citazione(rim, it["fonte"], it["testo"], it["cit"])
    if c.get("repose"):
        r = c["repose"]
        corpo += (f'<h3>Outer limit: <span data-v="{k}/r">{anni(r["anni"])}</span></h3><p>Even when the regular period has not run, the statute sets a '
                  f'final cut-off counted from the act or omission.</p>' + citazione(rim, r["fonte"], r["testo"], r["cit"]))
    corpo += f'<p>{h(esempio(k))}</p>'
    # calcolatore
    corpo += (f'<h2 id="calculator">Deadline calculator: {h(st["nome"])} {h(cc["breve"])}</h2><p>Enter the date to count from. '
              f'The calculator applies the general period{"s" if len(vs) > 1 else ""} above and nothing else.</p>' + calcolatore(s, ca))
    # eccezioni
    if c["eccezioni"]:
        corpo += f'<h2 id="exceptions">Exceptions and special rules for {h(cc["breve"])}</h2>'
        corpo += "".join(blocco_eccezione(rim, e) for e in c["eccezioni"])
    corpo += f'<h2 id="tolling">Rules that pause or extend deadlines in {h(st["nome"])}</h2>'
    if c.get("senza_regole_stato"):
        corpo += (f'<div class="nota">{ico("alert")}<p>The section for this claim applies “notwithstanding any other law”, so the general '
                  f'{h(st["nome"])} rules below may not apply to it in the same way. Ask a {h(st["nome"])} attorney.</p></div>')
    else:
        corpo += f'<p>These general rules apply to many {h(st["nome"])} deadlines, including this one, subject to their own conditions.</p>'
    corpo += "".join(blocco_eccezione(rim, e) for e in st["regole"])
    corpo += '<div class="ad-slot" aria-hidden="true"></div>'  # lontano dal risultato del calcolatore
    corpo += f'<h2 id="government">If the claim is against a government</h2>'
    corpo += "".join(blocco_eccezione(rim, e) for e in st["governo"])
    cambi = [x for x in st["cambi"] if (x["data"] == "2023-03-24" and any(v.get("prima") for v in vs)) or
             (x["data"] in ("2021-06-16", "2026-09-23") and any(v.get("transizione") for v in vs))]
    if cambi:
        corpo += '<h2 id="changes">Recent changes to this deadline</h2>' + "".join(blocco_cambio(rim, x) for x in cambi)
    corpo += box_affiliati("cella")
    # confronto e collegamenti
    corpo += (f'<h2 id="compare">{h(cc["nome"])} deadlines in other states</h2><p>The same type of claim has different deadlines from state to state. '
              f'<a href="/{ca}/">Compare all ten states</a>.</p>' + tabella_confronto(ca, attuale=s))
    altre = "".join(f'<li><a href="{url_cella(f"{s}/{x}")}">{h(CAUSE[x]["nome"])}</a></li>' for x in OC if x != ca and f"{s}/{x}" in CELLE)
    corpo += f'<h2>Other {h(st["nome"])} deadlines</h2><ul class="pillole">{altre}<li><a href="/{st["slug"]}/">All {h(st["nome"])} rules</a></li></ul>'
    faq, ld_faq = faq_blocco(k, rim)
    corpo += faq + rim.elenco()
    titolo = titolo_corto(f"{st['nome']} {cc['titolo']} Statute of Limitations ({breve.replace('years', 'Years').replace('year', 'Year')})",
                          f"{st['nome']} {cc['titolo']} Statute of Limitations",
                          f"{st['nome']} {cc['titolo']} Deadline to Sue")
    descr = descr_corta(
        f"{st['nome']} {cc['breve']} statute of limitations: {breve} under {prima_cit}. Statute text, when it starts, exceptions and a deadline calculator.",
        f"{st['nome']} {cc['breve']} deadline: {breve} ({prima_cit}). Statute text, exceptions and a deadline calculator.",
        f"{st['nome']} {cc['breve']}: {breve}. Statute text, exceptions and a deadline calculator.")
    pagina(f"{st['slug']}/{ca}/", titolo, descr, corpo, testata,
           briciole=[("Home", ""), (st["nome"], f"{st['slug']}/"), (cc["nome"], f"{st['slug']}/{ca}/")], jsonld=[ld_faq] if ld_faq else None)


# ---------------------------------------------------------------- pagina Stato
def pagina_stato(s):
    st = STATI[s]
    rim = Rimandi()
    testata = banda(st["nome"], f"{st['nome']} statutes of limitations for civil claims",
                    f"General deadlines to sue for six common claims under the {h(st['codice'])}, with the statute text, the rules that pause "
                    f"them and a calculator. Read on {data_lunga(LETTO)}.", icona="map")
    righe = []
    for ca in OC:
        k = f"{s}/{ca}"
        if k not in CELLE:
            righe.append(f'<tr><td>{h(CAUSE[ca]["nome"])}</td><td class="n">not published</td><td>{h(st.get("assente", {}).get(ca, ""))}</td></tr>')
            continue
        c = CELLE[k]
        per = "<br>".join(f'{cella_vs(v, k, i)} <small>{h(v["etichetta"])}</small>' for i, v in enumerate(c["varianti"]))
        cit = "<br>".join(h(v["cit"]) for v in c["varianti"])
        righe.append(f'<tr><td><a href="{url_cella(k)}">{h(CAUSE[ca]["nome"])}</a></td><td class="n">{per}</td><td>{cit}</td></tr>')
    corpo = (f'<div class="card pull"><p style="margin:0 0 10px">{h(st["nome"])} deadlines below are the general periods written in the statutes. '
             f'Each claim has its own page with the full text, exceptions and a calculator.</p>'
             f'<div class="tab"><table class="dati"><thead><tr><th>Claim</th><th>General period</th><th>Statute</th></tr></thead><tbody>{"".join(righe)}'
             f'</tbody></table></div></div>')
    corpo += avviso(st["nome"])
    corpo += (f'<h2 id="calculator">{h(st["nome"])} deadline calculator</h2><p>Choose the claim and the date to count from.</p>' + calcolatore(stato=s))
    corpo += f'<h2 id="tolling">Rules that pause or extend deadlines in {h(st["nome"])}</h2>'
    corpo += "".join(blocco_eccezione(rim, e) for e in st["regole"])
    corpo += '<div class="ad-slot" aria-hidden="true"></div>'  # lontano dal risultato del calcolatore
    corpo += f'<h2 id="government">Claims against a government in {h(st["nome"])}</h2>' + "".join(blocco_eccezione(rim, e) for e in st["governo"])
    if st["cambi"]:
        corpo += f'<h2 id="changes">Recent changes in {h(st["nome"])}</h2>' + "".join(blocco_cambio(rim, x) for x in st["cambi"])
    else:
        corpo += (f'<h2 id="changes">Recent changes in {h(st["nome"])}</h2><p>None of the periods on these pages changed in the statute versions we read; '
                  f'the sections show their own amendment history on the official site.</p>')
    for ca, motivo in st.get("assente", {}).items():
        corpo += f'<div class="nota info">{ico("info")}<p><strong>{h(CAUSE[ca]["nome"])}:</strong> {h(motivo)}</p></div>'
    altri = "".join(f'<li><a href="/{STATI[x]["slug"]}/">{h(STATI[x]["nome"])}</a></li>' for x in OS if x != s)
    corpo += f'<h2>Other states</h2><ul class="pillole">{altri}</ul>'
    faq, ld_faq = faq_blocco(s, rim)
    corpo += faq + rim.elenco()
    titolo = titolo_corto(f"{st['nome']} Statute of Limitations: Civil Deadlines by Claim", f"{st['nome']} Statutes of Limitations by Claim")
    descr = descr_corta(f"{st['nome']} statutes of limitations for personal injury, malpractice, wrongful death, debt, contracts and property damage, "
                        f"with statute text and a calculator.",
                        f"{st['nome']} civil statutes of limitations by claim, with the statute text, tolling rules and a deadline calculator.")
    pagina(f"{st['slug']}/", titolo, descr, corpo, testata, briciole=[("Home", ""), (st["nome"], f"{st['slug']}/")], jsonld=[ld_faq] if ld_faq else None)


# ---------------------------------------------------------------- pagina causa (confronto)
INTRO_CAUSA = {
    "personal-injury": "Personal injury covers claims for bodily harm caused by someone else, such as car accidents, falls and dog bites. Most states use one general period for these claims; some set a different one for intentional acts such as assault.",
    "medical-malpractice": "Claims against doctors, hospitals and other health care providers usually have their own rules: a short period, sometimes counted from discovery, and an outer limit (statute of repose) that can bar a claim even if the injury was found late.",
    "wrongful-death": "A wrongful death claim is brought after a death caused by someone else's wrongful act or negligence, usually by a personal representative or family members. Several states count the period from the date of death.",
    "debt": "These are the periods a creditor or debt buyer has to sue to collect a debt. Many states set different periods for written contracts, oral agreements, open accounts or credit cards. A federal rule forbids debt collectors to sue or threaten to sue on a consumer debt once the period has expired.",
    "breach-of-contract": "The deadline to sue for breach of contract often depends on whether the contract is written or oral. Some states use one period for both.",
    "property-damage": "Damage to a car, a house or other property can have a different deadline from an injury caused by the same event. Some states separate land (real property) from goods (personal property).",
}


def pagina_causa(ca):
    cc = CAUSE[ca]
    rim = Rimandi()
    tutti = [(s, v["anni"]) for s in OS if f"{s}/{ca}" in CELLE for v in CELLE[f"{s}/{ca}"]["varianti"]]
    minimo, massimo = min(a for _, a in tutti), max(a for _, a in tutti)
    st_min = sorted({STATI[s]["nome"] for s, a in tutti if a == minimo})
    st_max = sorted({STATI[s]["nome"] for s, a in tutti if a == massimo})
    sub = (f"General periods in ten states range from <strong>{anni(minimo, True)}</strong> ({h(', '.join(st_min))}) to "
           f"<strong>{anni(massimo, True)}</strong> ({h(', '.join(st_max))}). Statute text and exceptions for each state.")
    testata = banda(cc["nome"], f"{cc['nome']} statute of limitations by state", sub, icona="hourglass")
    corpo = (f'<div class="card pull"><p style="margin:0">{h(INTRO_CAUSA[ca])} This page compares ten states ({h(cc["esempi"])}).</p></div>')
    corpo += avviso()
    corpo += f'<h2 id="table">{h(cc["nome"])} deadlines in ten states</h2>' + tabella_confronto(ca)
    corpo += (f'<h2 id="calculator">Calculate a {h(cc["breve"])} deadline</h2>' + calcolatore())
    if ca == "debt":
        corpo += nota_debito()
    corpo += f'<h2 id="states">State by state</h2>'
    for n_stato, s in enumerate(OS):
        if n_stato == 3:
            corpo += '<div class="ad-slot" aria-hidden="true"></div>'  # lontano dal risultato del calcolatore
        k = f"{s}/{ca}"
        if k not in CELLE:
            continue
        c = CELLE[k]
        v = c["varianti"][0]
        corpo += (f'<h3><a href="{url_cella(k)}">{h(STATI[s]["nome"])}</a>: {cella_vs(v, k, 0)}'
                  f'{" (" + h(v["etichetta"].lower()) + ")" if len(c["varianti"]) > 1 else ""}</h3>'
                  + citazione(rim, v["fonte"], v["testo"], v["cit"]))
        if len(c["varianti"]) > 1:
            altre = "; ".join(f'{h(x["etichetta"].lower())}: {cella_vs(x, k, i + 1)} ({h(x["cit"])})' for i, x in enumerate(c["varianti"][1:]))
            corpo += f'<p class="small">Other periods: {altre}.</p>'
    if ca == "debt":
        corpo += '<h2 id="federal">The federal rule on time-barred debt</h2>' + blocco_eccezione(rim, N.REG_F)
    faq, ld_faq = faq_blocco(ca, rim)
    corpo += faq + rim.elenco()
    titolo = titolo_corto(f"{cc['titolo']} Statute of Limitations by State (10 States)", f"{cc['titolo']} Statute of Limitations by State")
    descr = descr_corta(f"{cc['nome']} statute of limitations by state: compare general periods in ten states, from {anni(minimo)} to {anni(massimo)}, "
                        f"with the statute text and exceptions.",
                        f"{cc['nome']} statute of limitations in ten states, from {anni(minimo)} to {anni(massimo)}, with statute text and exceptions.")
    pagina(f"{ca}/", titolo, descr, corpo, testata, briciole=[("Home", ""), (cc["nome"], f"{ca}/")], jsonld=[ld_faq] if ld_faq else None)


# ---------------------------------------------------------------- home
def home():
    rim = Rimandi()
    testata = banda("Ten states · six claims", "Statute of limitations by state: deadline calculator",
                    f"Find the general deadline to file a civil lawsuit in Texas, Florida, Ohio, Washington, Virginia, North Carolina, Michigan, "
                    f"Arizona, Massachusetts and Minnesota, from the statute text read on {data_lunga(LETTO)}.", icona="hourglass")
    corpo = f'<div class="pull">{calcolatore()}</div>'
    corpo += avviso()
    righe = []
    for s in OS:
        st = STATI[s]
        celle_html = []
        for ca in OC:
            k = f"{s}/{ca}"
            if k not in CELLE:
                celle_html.append('<td class="n">–</td>')
                continue
            vs = CELLE[k]["varianti"]
            celle_html.append('<td class="n"><a href="' + url_cella(k) + '">' + " / ".join(cella_vs(v, k, i) for i, v in enumerate(vs)) + "</a></td>")
        righe.append(f'<tr><td><a href="/{st["slug"]}/">{h(st["nome"])}</a></td>{"".join(celle_html)}</tr>')
    intest = "".join(f'<th class="n"><a href="/{ca}/">{h(CAUSE[ca]["nome"])}</a></th>' for ca in OC)
    corpo += (f'<h2 id="states">General deadlines at a glance</h2><p>Each cell links to the page with the statute text, exceptions and a calculator. '
              f'Where a cell shows two or more periods, the state uses different periods for different kinds of claim (for example written and oral '
              f'contracts).</p><div class="tab"><table class="dati"><thead><tr><th>State</th>{intest}</tr></thead><tbody>{"".join(righe)}</tbody>'
              f'<caption>Washington: no wrongful death page, because chapter 4.20 RCW does not state its own deadline.</caption></table></div>')
    corpo += '<div class="ad-slot" aria-hidden="true"></div>'
    corpo += ('<h2 id="how">How to read a statute of limitations</h2><div class="testo"><ul>'
              '<li><strong>The period</strong> is the time allowed to start the lawsuit, written in the statute (for example “within two years”).</li>'
              '<li><strong>The start date</strong> is when the claim “accrues”. Some statutes fix it (the date of death, the last payment); others leave it to the facts and the courts, such as when an injury was or should have been discovered.</li>'
              '<li><strong>Tolling</strong> pauses the clock, for example while the person with the claim is a minor or while the person being sued is out of state.</li>'
              '<li><strong>An outer limit</strong> (statute of repose) can bar a claim even if the injury was discovered late.</li>'
              '<li><strong>Claims against a government</strong> often need a written notice within months, long before the lawsuit deadline.</li></ul></div>')
    fl, oh = STATI["FL"]["cambi"][0], STATI["OH"]["cambi"][0]
    corpo += '<h2 id="changes">Recent changes some tables still miss</h2>' + blocco_cambio(rim, fl) + blocco_cambio(rim, oh)
    corpo += '<h2 id="claims">Compare by claim</h2><ul class="griglia">' + "".join(
        f'<li><a href="/{ca}/"><b>{h(CAUSE[ca]["nome"])}</b><span>{h(cap(CAUSE[ca]["esempi"]))}</span></a></li>' for ca in OC) + "</ul>"
    corpo += '<h2 id="all-states">Rules by state</h2><ul class="griglia">' + "".join(
        f'<li><a href="/{STATI[s]["slug"]}/"><b>{h(STATI[s]["nome"])}</b><span>{h(STATI[s]["codice"])}</span></a></li>' for s in OS) + "</ul>"
    faq, ld_faq = faq_blocco("home", rim)
    corpo += faq + rim.elenco()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}]
    if ld_faq:
        ld.append(ld_faq)
    pagina("", "Statute of Limitations by State: Civil Deadline Calculator",
           "Statute of limitations by state for personal injury, malpractice, wrongful death, debt, contracts and property damage, with statute text and a calculator.",
           corpo, testata.replace("{bc}", ""), jsonld=ld)


# ---------------------------------------------------------------- pagine istituzionali
def about():
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{NOME}</strong> is an independent publication, part of a small network of websites that turn official sources into '
             'plain-language guides. It shows the general deadlines to start common civil lawsuits in ten states, quoting the statute itself, '
             'linking to the legislature\'s official website and giving the date we read it.</p>'
             '<p>We are not lawyers and not a law firm, we do not give legal advice, and we do not answer questions about individual cases. '
             'Nothing on this site creates an attorney-client relationship. We do not refer readers to lawyers and are not paid by lawyers to '
             'recommend them.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Only periods that are written in a statute we have read, with the text quoted word for word.</li>'
             '<li>Where a statute does not state a deadline for a claim (Washington wrongful death, for example), we do not publish a page instead of guessing.</li>'
             '<li>Where a state has more than one possible period, we show all of them and say that an attorney can tell which one applies.</li>'
             '<li>Court decisions can change how a statute applies. We say so where we know a statute has been tested in court, but we do not summarize case law.</li></ul>'
             '<h2>Why only ten states</h2><div class="testo"><p>We started with states whose legislatures publish their codes in a form we can read and '
             'check automatically. California and New York are not included: their official code websites block automated reading, and we do not work '
             'around that.</p></div>'
             '<h2>How the site is paid for</h2><div class="testo"><p>The site shows advertising served by Google AdSense on pages with content. '
             'Advertisers do not choose or change what we publish. We do not run lead forms and do not sell or share anything you type.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, what it publishes and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", "About Statute of Limitations by State: an independent guide that quotes state statutes on civil deadlines; not a law firm.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")], pubblicita=False)


def come_controlliamo():
    rim = Rimandi()
    for fid in FONTI:
        rim.n(fid)
    n_cit = sum(len(v["testo"]) for c in CELLE.values() for v in c["varianti"])
    corpo = ('<div class="testo pull card">'
             f'<p>Every period on this site comes from a statute we downloaded from the official website of the state legislature (and, for the '
             f'federal debt rule, from the eCFR; one Washington court ruling comes from the state courts\' website). On {data_lunga(LETTO)} we saved {len(FONTI)} official pages and documents and recorded a fingerprint '
             f'of each. Before every update a separate program re-reads the saved copies, checks that each quotation appears word for word, and '
             f'reads the number of years again from the statute text to compare it with what each page shows.</p></div>')
    corpo += ('<h2>What we check</h2><ul class="testo">'
              f'<li><strong>Quotations</strong>: every quoted passage (the {n_cit} period quotations and all the exceptions) must appear in the saved official text.</li>'
              '<li><strong>Periods</strong>: the number of years is read again from the statute wording (“within two years”, “WITHIN FOUR YEARS”, “3 years”) and must match every page and the calculator.</li>'
              '<li><strong>Calculator</strong>: the code that runs in your browser is tested against an independent calculation on hundreds of dates, including 29 February and the dates when Florida and Ohio changed their law.</li>'
              '<li><strong>Dates read</strong>: each quotation shows when we read the official text. We re-read all statutes at least once a year and after each legislative session.</li></ul>')
    corpo += ('<h2>How the calculator counts</h2><div class="testo"><ul>'
              '<li>It adds the number of years in the statute to the date you enter (the same day and month). If you enter 29 February and the deadline year has no 29 February, it shows 28 February, the earlier date.</li>'
              '<li>It does not move a deadline that falls on a weekend or court holiday. Court rules sometimes do, but do not rely on it.</li>'
              '<li>Where a statute fixes a different start (Ohio consumer debt: 30 days after the last charge or payment) or a law changed the period for older claims (Florida negligence before March 24, 2023), it applies that rule. For Ohio contract claims that accrued before June 16, 2021 it shows no date and quotes the transition rule of Senate Bill 13 instead, because the deadline depends on the period that applied before.</li>'
              '<li>It does not compute notice deadlines for claims against a government: it lists the rules that the state page quotes.</li>'
              '<li>It does not apply tolling or exceptions: it lists them so you can ask an attorney.</li></ul></div>')
    corpo += ('<h2>What we do not do</h2><div class="testo"><p>We do not read or work around websites that block automated access (this is why '
              'California and New York are not on the site), and we do not publish a deadline that is not written in a statute. We do not summarize court '
              'decisions, with one exception: where a state supreme court has held a limit printed on this site unconstitutional (Washington, medical '
              'malpractice), we quote the holding and link the opinion on the court\'s own website, and still show the statute as printed.</p></div>')
    corpo += rim.elenco()
    testata = banda("How we check", "How we check every deadline", "Our sources, how we verify each quotation and period, and how the calculator counts.",
                    corta=True, icona="shield")
    pagina("how-we-check/", "How We Check Every Statute of Limitations",
           "How Statute of Limitations by State checks its data: official statute texts with fingerprints, every quote and period re-read, calculator tests.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")], pubblicita=False)


def privacy():
    affiliati = any(v.get("attivo") for k, v in AFF.items() if not k.startswith("_"))
    cookie = MON.privacy_cookie("en", SITO_ID, affiliati=affiliati)
    if not cookie:
        cookie = "<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. This site does not use profiling cookies and shows no advertising.</p>"
    california = MON.frase_california(SITO_ID) or "California residents: we do not sell or share personal information."
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {NOME} ({URL_SITO.replace("https://", "")}) collects. In short: very little, and nothing about your case.</p></div>'
             '<div class="testo"><h2>The calculator</h2><p>The deadline calculator runs entirely in your browser. The state, claim and date you choose are '
             'not sent to us or stored. There are no forms, accounts or newsletters on this site.</p>'
             '<h2>Your choices on the site</h2><p>The site remembers your choice of light or dark theme in your browser (local storage). Nothing else is '
             'stored on your device by us.</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             f'<h2>California</h2><p>{h(california)}</p>'
             f'<h2>Changes</h2><p>We update this page when the site changes. Last update: {data_lunga(LETTO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID, affiliati=affiliati) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", f"Privacy | {NOME}", f"Privacy at {NOME}: a calculator that runs in your browser, a cookie-free visit counter and Google AdSense with consent.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")], pubblicita=False)


def pagina_404():
    corpo = ('<div class="pull card"><p>The page you asked for does not exist. Try the <a href="/#calculator">deadline calculator</a> or one of the states below.</p></div>'
             '<ul class="griglia" style="margin-top:20px">' + "".join(
                 f'<li><a href="/{STATI[s]["slug"]}/"><b>{h(STATI[s]["nome"])}</b></a></li>' for s in OS) + "</ul>")
    testata = banda("404", "Page not found", "This address has no page.", corta=True, icona="alert")
    pagina("", f"Page not found | {NOME}", "Page not found on Statute of Limitations by State: try the deadline calculator or one of the ten states.",
           corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


# ---------------------------------------------------------------- file accessori
def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{LETTO.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in limits/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = limits/sito, Build command vuoto, Publish directory = "."
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
    for nome, t in ASSET.items():
        (SITO / "assets" / nome).write_text(t, encoding="utf-8")
    (SITO / "assets" / DATI_FILE).write_text(DATI_JS, encoding="utf-8")


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
    for s in OS:
        pagina_stato(s)
    for k in CELLE:
        pagina_cella(k)
    for ca in OC:
        pagina_causa(ca)
    about()
    come_controlliamo()
    privacy()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404 ({len(CELLE)} Stato × causa). Leggi lette il {data_lunga(LETTO)}.")


if __name__ == "__main__":
    main()
