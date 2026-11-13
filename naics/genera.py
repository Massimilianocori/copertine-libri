"""Genera il sito statico "NAICS Code Lookup" (inglese, pubblico USA) in naics/sito/: una pagina per settore, sottosettore,
gruppo di industrie e industria a sei cifre della classificazione NAICS 2022, con titoli e descrizioni ufficiali del Census
Bureau, voci dell'indice ufficiale, rimandi, codice 2017 e codici SIC 1987 collegati.

Uso (dalla radice del repository):
    python3 -I naics/raccolta/fonti.py        # scarica i file ufficiali -> raccolta/_grezzi/, dati/fonti.json
    python3 -I naics/raccolta/estrai.py       # legge i file -> dati/naics.json (si ferma se l'albero o i conteggi non tornano)
    python3 -I naics/raccolta/domanda.py      # ricerche vere (autocompletamento, gl=us) -> dati/domanda.json
    python3 naics/genera.py                   # pagine in naics/sito/
    python3 naics/verifica.py --browser       # controlli

Livelli e pagine (stessa lezione di ateco/, AdSense «scarso valore»):
- 2, 3, 4 e 6 cifre: una pagina ciascuno (/54/, /541/, /5415/, /541511/; settori a intervallo /31-33/).
- 5 cifre: nessuna pagina. Se l'industria a 5 cifre ha un solo figlio (522 casi su 689: stesso titolo, codice + «0», la
  descrizione ufficiale dice «See industry description for …») il suo indirizzo è la pagina a 6 cifre. Se ha più figli
  (167 casi) è un capitolo con ancora nella pagina del gruppo a 4 cifre (/5415/#n-54151): descrizione, esempi e rimandi.
- Ogni pagina di codice si indicizza solo se ha abbastanza testo proprio (MIN_PAROLE_PROPRIE, MAX_SOVRAPPOSIZIONE): le altre
  restano consultabili, noindex, fuori dalla sitemap e senza pubblicità.
"""
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from html import escape, unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import stile  # noqa: E402

URL_SITO = "https://naics-code-lookup.netlify.app"  # unico punto da cambiare (anche in verifica.py) se il nome su Netlify è diverso
NOME = "NAICS Code Lookup"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti della rete)
GOOGLE_VERIFICA_2 = "fCopHfbOO5n6WfdF7-ZnrX4BCGXMGDkT_Qfsb4lKR4o"  # Search Console, tag della proprietà nuova: non rimuoverlo
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "naics"  # nome del sito in monetizzazione.json
MIN_PAROLE_ADSENSE = 400  # niente pubblicità nelle pagine noindex o con poco testo
MIN_PAROLE_PROPRIE = 120  # gruppi di 5 parole che non compaiono in nessun'altra pagina di codice: sotto, noindex
MAX_SOVRAPPOSIZIONE = 0.55  # quota del testo in comune con la pagina di codice più simile: da qui in su, noindex
MIN_PROPRIE_RICHIESTA = 60  # pagine a 6 cifre con domanda dimostrata (dati/richieste.json): soglia più bassa, perché la descrizione ufficiale è corta
MAX_SOVRAPPOSIZIONE_RICHIESTA = 0.65
MAX_SOVRAPPOSIZIONE_ATTIVITA = 0.40  # pagine «NAICS code for …» (revisione del 13/11 sera): più severa, una guida che ripete la pagina di settore resta noindex
QUOTA_MODELLO = 0.05  # gruppi di 5 parole presenti in almeno il 5% delle pagine di codice = modello della pagina, esclusi dalla misura
FRASE_FISSA = "check with the agency or form that asks for the code"
FILE_VOLUMI_ATTIVITA = "volumi-attivita-2026-11-13.json"  # misura con data: per rifarla, file nuovo con la data e nome qui (e in verifica.py)
MIN_VOLUME_ATTIVITA = 100  # pagina «NAICS code for …» solo con almeno 100 ricerche al mese misurate su una delle sue frasi
QUOTA_MODELLO_ATTIVITA = 0.25  # gruppi di 5 parole presenti in almeno un quarto delle pagine attività = modello della pagina
SOGLIA_SETTORE_COMPLETO = 40  # nella pagina attività di un settore: ogni codice a 6 cifre se sono al massimo 40, altrimenti 2 esempi per sottosettore

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
LIVELLO = {2: "Sector", 3: "Subsector", 4: "Industry group", 5: "NAICS industry", 6: "National industry"}


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
NA = carica("naics.json")
DOM = carica("domanda.json")
VOL = carica("volumi.json")
VOLA = carica(FILE_VOLUMI_ATTIVITA)
ATT = carica("attivita.json")["attivita"]
FAQ = carica("faq.json")["faq"]
RICH = carica("richieste.json")["codici"]
C = NA["codici"]
ORDINE = NA["ordine"]
SIC = NA["sic"]
SIC22 = NA["sic_di_22"]
GS = NA["gruppi_sic"]
CONTROLLO = max(date.fromisoformat(x["letto_il"]) for x in FJ["file"].values())


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def num(n):
    return f"{n:,}"


def accorcia(s, n):
    if len(s) <= n:
        return s
    t = s[:n - 1].rsplit(" ", 1)[0].rstrip(",;:(-– ")
    return t + "…"


# ---------------------------------------------------------------- albero
FIGLI = defaultdict(list)
for _c in ORDINE:
    if C[_c]["p"]:
        FIGLI[C[_c]["p"]].append(_c)
LIV = defaultdict(list)
for _c in ORDINE:
    LIV[C[_c]["l"]].append(_c)
SETTORI, SOTTO, GRUPPI, CINQUE, SEI = LIV[2], LIV[3], LIV[4], LIV[5], LIV[6]


def antenato(c, l):
    while C[c]["l"] > l:
        c = C[c]["p"]
    return c


def sei_di(c):
    if C[c]["l"] == 6:
        return [c]
    return [x for f in FIGLI[c] for x in sei_di(f)]


def unico(c5):
    """Industria a 5 cifre con un solo figlio: la sua pagina è quella del figlio."""
    return len(FIGLI[c5]) == 1


def url_di(c):
    l = C[c]["l"]
    if l == 5:
        return url_di(FIGLI[c][0]) if unico(c) else f"/{c[:4]}/#n-{c}"
    return f"/{c}/"


def percorso_pagina(c):
    return url_di(c).split("#")[0].lstrip("/")


def titolo_breve(c):
    return C[c]["t"]


# ---------------------------------------------------------------- concordanze
DA17 = defaultdict(list)  # 2022 -> [(2017, pezzo)]
for a, b, t in NA["c22_17"]:
    DA17[a].append((b, t))
A22 = defaultdict(list)  # 2017 -> [2022]
T17 = NA["titoli_2017"]
for a, t, b in NA["c17_22"]:
    if b not in A22[a]:
        A22[a].append(b)
INDICATORE = {"*": "Title changed in 2022, content unchanged", "**": "New code in 2022",
              "***": "2017 code reused in 2022 with a change of content",
              "****": "2017 code reused; content changed at a lower level with insignificant impact here"}


def stato_2017(c):
    """Come è cambiato il codice 2022 c rispetto al 2017 (dal confronto della concordanza)."""
    v = DA17[c]
    vecchi = [b for b, _ in v]
    if vecchi == [c] and A22[c] == [c]:
        return "same"
    return "changed"


# ---------------------------------------------------------------- fonti e rimandi
FONTI_DEF = {fid: {"titolo": f["titolo"], "chi": f["chi"], "url": f["url"], "letto": f["letto_il"]} for fid, f in FJ["file"].items()}


class Rimandi:
    def __init__(self):
        self.ordine = []

    def ref(self, ids):
        if isinstance(ids, str):
            ids = [ids]
        nums = []
        for i in ids:
            if i not in FONTI_DEF:
                raise SystemExit(f"unknown source: {i}")
            if i not in self.ordine:
                self.ordine.append(i)
            nums.append(self.ordine.index(i) + 1)
        return '<sup class="ref">' + ",".join(f'<a href="#f{n}" aria-label="source {n}">[{n}]</a>' for n in sorted(set(nums))) + "</sup>"

    def elenco(self):
        if not self.ordine:
            return ""
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = FONTI_DEF[i]
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}.</li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2><ol>{"".join(voci)}</ol>'
                f'<p class="small">Files read on {data_lunga(CONTROLLO)}. Official texts are reproduced without changes. <a href="/how-we-check/">How we check</a>.</p></section>')


ATTRIBUZIONE = ("Codes, titles, descriptions, index entries and concordances: U.S. Census Bureau, North American Industry Classification "
                "System (NAICS) 2022 files and the official concordances back to the 1987 SIC (public domain). Official texts are shown "
                "without changes; layout, links, counts and the chaining of concordances from 1997 to 2022 are ours.")


# ---------------------------------------------------------------- risorse
def _impronta(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:10]


CSS = re.sub(r"\n", "", stile.CSS)
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' + "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in stile.ICONE.items()) + "</svg>\n")
APP_JS = stile.APP_JS.strip() + "\n"
ASSET = {f"site.{_impronta(CSS)}.css": CSS, f"app.{_impronta(APP_JS)}.js": APP_JS,
         f"favicon.{_impronta(stile.FAVICON_SVG)}.svg": stile.FAVICON_SVG, f"icons.{_impronta(SPRITE)}.svg": SPRITE}
CSS_FILE, JS_FILE, FAVICON_FILE, ICONS_FILE = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="34" height="34" alt="">'


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- scheletro
URLS = []
INDICIZZA = {}
INDICIZZA_ATT = {}  # pagine «NAICS code for …»: stessa regola del testo proprio (misura_attivita)
_PROVA = None
MENU = [("#sectors", "Sectors"), ("naics-code-for/", "By activity"), ("naics-2017-to-2022/", "2017 → 2022"), ("sic-to-naics/", "SIC to NAICS"), ("how-we-check/", "How we check")]
DISCLAIMER = ("<strong>Information from the official Census Bureau NAICS files, not legal, tax or business advice.</strong> The right code depends "
              f"on the primary activity of your establishment, and each agency assigns codes with its own method: {FRASE_FISSA}. Independent "
              "site, not affiliated with the U.S. Census Bureau, the Office of Management and Budget, the IRS or the SBA.")


def parole_principali(corpo):
    t = re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    return len(re.findall(r"\w+", t))


def menu_html(percorso):
    out = ""
    for u, t in MENU:
        cur = ' aria-current="page"' if (percorso and not u.startswith("#") and percorso.startswith(u)) else ""
        out += f'<a href="/{u}"{cur}>{h(t)}</a>'
    return out


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
    if _PROVA is not None:
        _PROVA[percorso] = testata + corpo
        return
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append(percorso)
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": i, "name": n, "item": f"{URL_SITO}/{p}"} for i, (n, p) in enumerate(briciole, 1)]
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb">' + " › ".join([f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    con_pub = indicizza and parole_principali(testata + corpo) >= MIN_PAROLE_ADSENSE
    adsense = MON.script_adsense(SITO_ID, con_pub)
    corpo_tr = corpo + MON.riga_trasparenza(corpo, "en")
    testo = f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA_2}">{adsense}
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
<meta name="theme-color" content="#0E2B33">
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
<a class="logo" href="/">{LOGO}<span>NAICS <b>Code</b> Lookup</span></a>
<nav class="menu" aria-label="Main">{menu_html(percorso)}</nav>
<button type="button" class="tema" data-tema aria-label="Light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
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
<a class="logo" href="/">{LOGO}<span>NAICS <b>Code</b> Lookup</span></a>
<p><strong>{NOME}</strong> turns the official NAICS 2022 files of the U.S. Census Bureau into readable pages: titles, descriptions, the
activities of the official index, the 2017 codes and the 1987 SIC codes. Independent site, not affiliated with the Census Bureau, OMB, the IRS or the SBA.</p>
<p>{ATTRIBUZIONE}</p>
</div><div>
<h2>Codes</h2><ul><li><a href="/#search">Search a code</a></li><li><a href="/#sectors">All 20 sectors</a></li>
<li><a href="/naics-2017-to-2022/">NAICS 2017 to 2022</a></li><li><a href="/sic-to-naics/">SIC to NAICS</a></li></ul>
</div><div>
<h2>The site</h2><ul><li><a href="/how-we-check/">How we check</a></li><li><a href="/how-we-check/#corrections">Report an error</a></li>
<li><a href="/about/">About</a></li><li><a href="/privacy/">Privacy</a></li></ul>
</div></div>
<p class="f-base">General information from the official classification files, not advice: {FRASE_FISSA}. The original classification is on the
<a href="https://www.census.gov/naics/" rel="noopener">Census Bureau website</a>.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="tree"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def tabella(intest, righe, caption="", num_=None, attr=None, id_=None, resp="", classe=""):
    num_ = num_ or []
    th = "".join(f'<th scope="col"{" class=\"n\"" if i in num_ else ""}>{x}</th>' for i, x in enumerate(intest))
    etich = [re.sub(r"<[^>]+>", "", x) for x in intest]
    body = ""
    for k, r in enumerate(righe):
        at = attr[k] if attr else ""
        body += f"<tr{at}>" + "".join(f'<td{" class=\"n\"" if i in num_ else ""}{f" data-l=\"{h(etich[i])}\"" if resp and i else ""}>{x}</td>'
                                      for i, x in enumerate(r)) + "</tr>"
    cap = f"<caption>{caption}</caption>" if caption else ""
    idt = f' id="{id_}"' if id_ else ""
    cl = " ".join(x for x in ("dati", resp, classe) if x)
    return f'<div class="tab"><table class="{cl}"{idt}>{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def nota(testo, tipo="info", icona="info"):
    return f'<div class="nota {tipo}">{ico(icona)}<p>{testo}</p></div>'


def faq_html(voci, titolo="Frequently asked questions"):
    if not voci:
        return "", None
    blocchi = "".join(f'<div class="faq"><h3>{h(q)}</h3><p>{h(a)}{ref}</p></div>' for q, a, ref in voci)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a, _ in voci]}
    return (f'<h2 id="faq">{h(titolo)}</h2><p class="small">Questions people really search on Google, answered from the official sources cited.</p>'
            + blocchi), ld


def link_cod(c, testo=None):
    return f'<a class="cod" href="{url_di(c)}">{h(testo or c)}</a>'


RE_CODICE = re.compile(r"\b((?:U\.S\. )?Industry Group|(?:U\.S\. )?Industry|Industries|Subsector|Sector)\s+(\d{2,6}(?:-\d{2})?)\b")


def linkifica(testo):
    """Collega i codici citati nei testi ufficiali («U.S. Industry 111191», «Subsector 522», «Sector 56») e i codici a 4-6 cifre."""
    t = h(testo)

    def sost(m):
        c = m.group(2)
        return f"{m.group(1)} {link_cod(c)}" if c in C else m.group(0)
    t = RE_CODICE.sub(sost, t)
    return re.sub(r"(?<![\w/#>-])(\d{4,6})(?![\w<-])", lambda m: link_cod(m.group(1)) if m.group(1) in C else m.group(1), t)


# ---------------------------------------------------------------- domanda dimostrata (suggerimenti veri di Google)
PAROLE_VUOTE = {"naics", "naic", "sic", "code", "codes", "number", "lookup", "for", "a", "an", "the", "and", "of", "in", "business", "company", "service",
                "services", "shop", "store", "2022"}


def codici_richiesti():
    """{codice a 6 cifre: suggerimento salvato}. Si ferma se una voce di richieste.json non regge."""
    tutte = {s for v in DOM["radici"].values() for s in v}
    out = {}
    for s in sorted(tutte):
        for c in re.findall(r"(?<!\d)\d{6}(?!\d)", s):
            if c in C and C[c]["l"] == 6:
                out.setdefault(c, s)
    for c, s in RICH.items():
        if c not in C or C[c]["l"] != 6:
            raise SystemExit(f"richieste.json: {c} non è un codice a 6 cifre del 2022")
        if s not in tutte:
            raise SystemExit(f"richieste.json: «{s}» non è tra i suggerimenti salvati in domanda.json")
        parole = {w for w in re.findall(r"[a-z]+", s.lower()) if w not in PAROLE_VUOTE}
        testo = set(re.findall(r"[a-z]+", " ".join([C[c]["t"]] + C[c]["d"] + C[c]["idx"] + C[c]["es"]).lower()))
        if not parole or any(not any(x.startswith(w[:5]) for x in testo) for w in parole):
            raise SystemExit(f"richieste.json: «{s}» non corrisponde al titolo, alla descrizione o all'indice ufficiale di {c}")
        out[c] = s
    return out


RICHIESTI = codici_richiesti()

# ---------------------------------------------------------------- rimandi ufficiali di altri codici che puntano a un codice a 6 cifre
ARRIVI = defaultdict(list)  # 6 cifre -> [(codice che manda, frase ufficiale)]
for _c in ORDINE:
    if C[_c]["l"] == 5 and unico(_c):
        continue  # stesso testo del figlio a 6 cifre
    for _x in C[_c]["xr"]:
        _visti = set()
        for _n in re.findall(r"(?<![\w/#-])(\d{5,6})(?![\w-])", _x):
            if _n in C and C[_n]["l"] == 5 and unico(_n):
                _n = FIGLI[_n][0]
            if _n in C and C[_n]["l"] == 6 and _n != _c and C[_n]["p"] != _c and _n not in _visti:
                _visti.add(_n)
                ARRIVI[_n].append((_c, _x))

# ---------------------------------------------------------------- SIC: righe principali e righe che condividono solo un pezzo
AVANTI97, T97 = {}, {}  # codice NAICS 1997 -> codici 2022 raggiunti (catena ufficiale); titolo 1997
for _s, _v in SIC.items():
    for _x in _v["n97"]:
        AVANTI97[_x["n"]] = _x["n22"]
        T97[_x["n"]] = re.sub(r"\s*\(pt\)\s*$", "", _x["t97"]).strip()
T97.update(NA["titoli_1997"])  # titolo del file 1997 NAICS → SIC (quello del file SIC → NAICS ha qualche variante)


def sic_righe(c):
    """(principali, altre, motivi) per un codice 2022. Diretto: tutte principali. Via catena: principale la riga il cui codice 1997 è
    finito tutto in c («whole») o aveva lo stesso titolo («title»); le altre condividono solo un pezzo dell'industria del 1997."""
    s = SIC22[c]
    if s["diretto"]:
        return list(s["righe"]), [], {}
    princ, altre, motivi = [], [], {}
    for x in s["righe"]:
        n = x["n97"]
        if AVANTI97.get(n) == [c]:
            motivi[n] = "whole"
            princ.append(x)
        elif T97.get(n, "").lower() == C[c]["t"].lower():
            motivi[n] = "title"
            princ.append(x)
        else:
            altre.append(x)
    return princ, altre, motivi


def sic_in_breve(c, n=3):
    """Testo corto per la scheda: i SIC principali, oppure quelli parziali dichiarati come tali."""
    princ, altre, _ = sic_righe(c)
    if not princ and not altre:
        return "none"
    righe = princ or altre
    sics = sorted({x["sic"] for x in righe})
    if not princ and len(sics) > 6:
        return f"{len(sics)} codes (partial)"
    return ", ".join(sics[:n]) + ("…" if len(sics) > n else "") + ("" if princ else " (partial)")


# ---------------------------------------------------------------- numeri e segnaposti
SEI6_NUOVI = [c for c in SEI if C[c]["ind"] == "**"]
N17 = sorted(A22)
N17_STESSI = [c for c in N17 if A22[c] == [c] and [b for b, _ in DA17[c]] == [c]]
_sett_nuovi = Counter(antenato(c, 2) for c in SEI6_NUOVI).most_common(1)[0]
NUM = {f"n_{l}": num(len(LIV[l])) for l in range(2, 7)}
NUM.update({"n_codici": num(len(C)), "n_idx": num(NA["numeri"]["righe_indice"]), "n_sic": num(len(SIC)),
            "n6_nuovi": num(len(SEI6_NUOVI)), "n6_riusati": num(sum(1 for c in SEI if C[c]["ind"] == "***")),
            "n6_titolo": num(sum(1 for c in SEI if C[c]["ind"] == "*")),
            "sett_piu_nuovi": f"{_sett_nuovi[0]} «{C[_sett_nuovi[0]]['t']}» ({_sett_nuovi[1]} new codes)",
            "n17": num(len(N17)), "n17_stessi": num(len(N17_STESSI)), "n17_altri": num(len(N17) - len(N17_STESSI)),
            "n_454110": str(len(A22["454110"])), "controllo": data_lunga(CONTROLLO)})


class Segnaposti(dict):
    """Numeri del sito più titoli ufficiali: {t_541611} = titolo NAICS 2022, {sic_8742} = titolo SIC, {gs_73} = gruppo SIC."""

    def __missing__(self, k):
        if k.startswith("t_") and k[2:] in C:
            return C[k[2:]]["t"]
        if k.startswith("sic_") and k[4:] in SIC:
            return SIC[k[4:]]["t"]
        if k.startswith("gs_") and k[3:] in GS:
            return GS[k[3:]]
        raise SystemExit(f"segnaposto sconosciuto: {k}")


def riempi(t, extra=None):
    m = Segnaposti(NUM)
    m.update(extra or {})
    out = t.format_map(m)
    controlla_titoli_citati(out, t[:40])
    return out


def controlla_titoli_citati(testo, dove):
    """Ogni «codice «titolo»» scritto da noi deve avere il titolo ufficiale (NAICS 2022 o gruppo/codice SIC)."""
    for cod, tit in re.findall(r"(?<![\d-])(\d{2,6}(?:-\d{2})?) «([^»]+)»", testo):
        ok = (cod in C and C[cod]["t"] == tit) or (cod in SIC and SIC[cod]["t"] == tit) or (cod in GS and GS[cod] == tit)
        if not ok:
            raise SystemExit(f"{dove}: il titolo citato per {cod} («{tit}») non è quello ufficiale")


def frasi_misurate():
    """{frase: volume} di tutte le frasi con un volume misurato (> 0): frasi chieste allo strumento e frasi simili che ha restituito."""
    out = {f: v["volume"] for f, v in VOL["frasi"].items() if v.get("volume")}
    for f, v in VOLA["frasi"].items():
        for s, n in (v.get("simili") or {}).items():
            if n:
                out.setdefault(s, n)
        if v.get("volume"):
            out[f] = v["volume"]
    return out


MISURATE = frasi_misurate()


def faq_pagina(pid, rim, extra=None):
    voci = []
    tutte = {s for v in DOM["radici"].values() for s in v}
    for x in FAQ:
        if x["pagina"] != pid:
            continue
        if pid.startswith("naics-code-for-") and not MISURATE.get(x["ricerca"]):
            raise SystemExit(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non ha un volume misurato (pagine attività: solo ricerche misurate)")
        if x["ricerca"] not in tutte and not MISURATE.get(x["ricerca"]):
            raise SystemExit(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non è tra i suggerimenti salvati né tra le ricerche misurate")
        voci.append((x["q"], riempi(x["a"], extra), rim.ref(x["fonti"])))
    return voci


# ---------------------------------------------------------------- blocchi di una pagina di codice
def paragrafi(c):
    return "".join(f"<p>{linkifica(p)}</p>" for p in C[c]["d"])


def blocco_esempi(c, hn="h3"):
    if not C[c]["es"]:
        return ""
    return (f'<{hn} id="examples-{c}">Illustrative examples</{hn}><ul class="lista-idx">'
            + "".join(f"<li>{h(e)}</li>" for e in C[c]["es"]) + "</ul>")


def blocco_rimandi(c, hn="h3"):
    v = C[c]
    if not v["xr"]:
        return ""
    lead = v.get("xr_lead") or "Establishments primarily engaged in"
    return (f'<{hn} id="not-here-{c}">Classified elsewhere (cross-references)</{hn}><p class="small">{h(lead)}:</p><ul>'
            + "".join(f"<li>{linkifica(x)}</li>" for x in v["xr"]) + "</ul>")


def blocco_indice(c, rim):
    v = C[c]
    if not v["idx"]:
        return ('<h2 id="index">Official index entries</h2><p>The official 2022 index has no entry pointing to this code: read the description '
                f'above.{rim.ref("indice")}</p>')
    return (f'<h2 id="index">{num(len(v["idx"]))} activities in the official index</h2><p class="small">Each line is an entry of the Census Bureau\'s '
            f'2022 NAICS index that is classified in {c}.{rim.ref("indice")}</p><ul class="lista-idx">'
            + "".join(f"<li>{h(e)}</li>" for e in v["idx"]) + "</ul>")


def blocco_2017(c, rim):
    v = C[c]
    righe = DA17[c]
    ind = v["ind"]
    if stato_2017(c) == "same" and not ind:
        return (f'<h2 id="naics-2017">NAICS 2017</h2><p>Same code and same content in NAICS 2017: {c} «{h(T17.get(c, v["t"]))}».'
                f'{rim.ref("c22_17")}</p>')
    testa = f'<h2 id="naics-2017">NAICS 2017 code{"s" if len(righe) > 1 else ""}</h2>'
    if ind:
        testa += f'<p><span class="tag car">{h(INDICATORE[ind])}</span>{rim.ref("struttura")}</p>'
    rr = []
    for b, t in righe:
        divisi = [x for x in A22.get(b, []) if x != c]
        altro = (f'<small>The 2017 code also went to {", ".join(link_cod(x) for x in divisi)}</small>' if divisi else "")
        rr.append([f'<a class="cod" href="/naics-2017-to-2022/#v-{b}">{b}</a>', h(t) + altro])
    return (testa + f'<p class="small">Official 2022 → 2017 concordance: the 2017 industries, or pieces of them, that make up {c}.{rim.ref("c22_17")}</p>'
            + tabella(["2017 code", "2017 title (piece moved)"], rr))


def blocco_arrivi(c, rim):
    v = ARRIVI.get(c)
    if not v:
        return ""
    voci = [f'<li><span class="mini">In {link_cod(a)} {h(C[a]["t"])}:</span> {linkifica(x)}</li>' for a, x in v]
    lista = '<ul class="arrivi">' + "".join(voci) + "</ul>"
    if len(voci) > 10:
        lista = f'<details class="tutte"><summary>Show all {len(voci)} cross-references</summary>{lista}</details>'
    # testo ripreso da altre pagine: marcato, così la misura dell'indicizzazione non lo conta come contenuto proprio
    return (f'<section data-ripreso><h2 id="sent-here">What other industries send to {c}</h2><p class="small">Cross-references written in the official '
            f'descriptions of other codes that name {c}: activities those industries exclude and classify here.{rim.ref("rimandi")}</p>{lista}</section>')


def _tab_sic(righe, motivi=None, con_via=False):
    rr = []
    for x in righe:
        note = []
        if x["parte"]:
            note.append("Part of the SIC industry")
        if con_via:
            n = x["n97"]
            m = (motivi or {}).get(n)
            perche = {"whole": ": the whole 1997 industry is now in this code", "title": ": same title in 1997"}.get(m, "")
            note.append(f'Via 1997 NAICS {n} {h(T97.get(n, ""))}{perche}')
        rr.append([f'<a class="cod" href="/sic-to-naics/#sic-{x["sic"]}">{x["sic"]}</a>', h(x["t"]) + "".join(f"<small>{y}</small>" for y in note)])
    return tabella(["SIC 1987", "SIC title"], rr, classe="sic-tab")


def blocco_sic(c, rim):
    s = SIC22[c]
    righe = s["righe"]
    if not righe:
        return (f'<h2 id="sic">SIC code</h2><p>The Census concordances do not link this industry to any 1987 SIC code.'
                f'{rim.ref(["naics97_sic", "c22_17"])}</p>')
    princ, altre, motivi = sic_righe(c)
    if s["diretto"]:
        sics = sorted({x["sic"] for x in righe})
        tab = _tab_sic(righe)
        if len(righe) > 8:
            tab = f'<details class="tutte"><summary>Show all {len(righe)} SIC lines</summary>{tab}</details>'
        return (f'<h2 id="sic">SIC code{"s" if len(sics) > 1 else ""}: {", ".join(sics[:6])}{"…" if len(sics) > 6 else ""}</h2>'
                f'<p class="small">This industry has the same code and the same content since NAICS 1997, so the official Census concordance between '
                f'1987 SIC and 1997 NAICS applies as it is.{rim.ref("naics97_sic")}</p>' + tab)
    fonti = rim.ref(["c22_17", "c97_02", "naics97_sic"])
    spiega = (f"There is no official SIC line for {c}: the only official Census concordance is between 1987 SIC and 1997 NAICS, and this industry "
              f"changed after 1997. The SIC codes below are our derivation: we followed the official concordances 2022 → 2017 → 2012 → 2007 → 2002 → "
              f"1997 back to {len(s['n97'])} NAICS 1997 {'industry and took its' if len(s['n97']) == 1 else 'industries and took their'} official SIC lines.{fonti}")
    out = ""
    if princ:
        sics = sorted({x["sic"] for x in princ})
        out += (f'<h2 id="sic">SIC code{"s" if len(sics) > 1 else ""}: {", ".join(sics[:6])}{"…" if len(sics) > 6 else ""}</h2><p class="small">{spiega}</p>'
                f'<h3 id="sic-closest">Closest SIC codes</h3><p class="small">SIC lines of the 1997 industries that are now entirely inside {c}, or that had '
                f'the same title.</p>' + _tab_sic(princ, motivi, True))
        if altre:
            n_s = len({x["sic"] for x in altre})
            tab = _tab_sic(altre, motivi, True)
            out += (f'<h3 id="sic-partial">SIC codes that share only a piece</h3><p class="small">{n_s} more SIC code{"s" if n_s != 1 else ""} reached through 1997 '
                    f'industries of which only a piece is in {c}; the rest went to other 2022 codes. Most activities of these SIC codes are <strong>not</strong> '
                    f'in this industry: read the part descriptions.</p>'
                    f'<details class="tutte"><summary>Show {len(altre)} partial SIC line{"s" if len(altre) != 1 else ""}</summary>{tab}</details>')
        return out
    sics = sorted({x["sic"] for x in altre})
    tab = _tab_sic(altre, motivi, True)
    if len(altre) > 8:
        tab = f'<details class="tutte"><summary>Show all {len(altre)} partial SIC lines</summary>{tab}</details>'
    testa = ("SIC codes: no single equivalent" if len(sics) > 6 else
             f'SIC code{"s" if len(sics) > 1 else ""} (partial match): {", ".join(sics)}')
    return (f'<h2 id="sic">{testa}</h2><p class="small">{spiega}</p><p class="small">Only a piece of {"that 1997 industry" if len(s["n97"]) == 1 else "each of those 1997 industries"} '
            f'is in {c} (the rest went to other 2022 codes), so {"the SIC code" if len(sics) == 1 else f"each of the {len(sics)} SIC codes"} below matches this '
            f'industry only in part: read the part descriptions.</p>' + tab)


def fatti(c):
    v = C[c]
    l = v["l"]
    celle = [("Code", f'<span class="cod">{c}</span>'), ("Level", LIVELLO[l] + (" (U.S.)" if l == 6 and not c.endswith("0") else ""))]
    if l == 6:
        p5 = v["p"]
        celle.append(("NAICS industry", f'<span class="cod">{p5}</span> (same)' if unico(p5) else link_cod(p5)))
        celle.append(("2017 code", ", ".join(b for b, _ in DA17[c][:3]) + ("…" if len(DA17[c]) > 3 else "")))
        celle.append(("SIC 1987", sic_in_breve(c)))
    else:
        celle.append(("Six-digit codes", num(len(sei_di(c)))))
    if l >= 3:
        s = antenato(c, 2)
        celle.append(("Sector", f'<a class="cod" href="{url_di(s)}">{s}</a>'))
    if v.get("T"):
        celle.append(("Canada and Mexico", "Comparable (T)"))
    return '<div class="card pull fatti">' + "".join(f'<div class="fatto"><span>{a}</span><b>{b}</b></div>' for a, b in celle) + "</div>"


def briciole_di(c):
    voci = [("Home", "")]
    for l in range(2, C[c]["l"] + 1):
        a = antenato(c, l)
        if C[a]["l"] == 5 and unico(a):
            continue
        if C[a]["l"] == 5:
            continue
        voci.append((a, percorso_pagina(a)))
    return voci


def titolo_pagina(c, prefisso):
    t = f"{prefisso}{c}: {C[c]['t']}"
    if len(t) <= 65:
        return t
    return f"{prefisso}{c}: " + accorcia(C[c]["t"], 65 - len(prefisso) - len(c) - 2)


def descr_pagina(c, coda):
    base = f"NAICS {c} {C[c]['t']}: "
    d = base + coda
    if len(d) <= 160:
        return d
    return f"NAICS {c} " + accorcia(C[c]["t"], 160 - len(coda) - len(c) - 9) + ": " + coda


def albero_figli(c, mostra_sei=True):
    out = '<ul class="albero">'
    for f in FIGLI[c]:
        if C[f]["l"] == 5 and unico(f):
            f6 = FIGLI[f][0]
            out += f'<li>{link_cod(f6)}<span>{h(C[f6]["t"])}</span></li>'
            continue
        extra = ""
        if mostra_sei and C[f]["l"] == 5:
            extra = f'<span class="mini">{", ".join(link_cod(x) for x in FIGLI[f])}</span>'
        elif C[f]["l"] < 5:
            extra = f'<span class="mini">{num(len(sei_di(f)))} six-digit code{"s" if len(sei_di(f)) != 1 else ""}</span>'
        out += f'<li>{link_cod(f)}<span>{h(C[f]["t"])}</span>{extra}</li>'
    return out + "</ul>"


# ---------------------------------------------------------------- pagine di codice
def pagina_sei(c):
    rim = Rimandi()
    v = C[c]
    corpo = fatti(c)
    corpo += f'<h2 id="description">Official description</h2><div class="testo">{paragrafi(c)}</div><p class="small">2022 NAICS description, U.S. Census Bureau.{rim.ref("descrizioni")}</p>'
    corpo += blocco_esempi(c, "h2")
    corpo += blocco_indice(c, rim)
    corpo += blocco_rimandi(c, "h2")
    if v["xr"]:
        corpo += f'<p class="small">Cross-references from the official 2022 file.{rim.ref("rimandi")}</p>'
    corpo += blocco_arrivi(c, rim)
    corpo += blocco_2017(c, rim)
    corpo += blocco_sic(c, rim)
    p5 = v["p"]
    g4 = antenato(c, 4)
    corpo += blocco_guide(c)
    corpo += f'<h2 id="hierarchy">Where {c} sits in NAICS</h2><ul class="albero">'
    for l in (2, 3, 4):
        a = antenato(c, l)
        corpo += f'<li>{link_cod(a)}<span>{h(C[a]["t"])}</span><span class="mini">{LIVELLO[l]}</span></li>'
    if not unico(p5):
        corpo += f'<li>{link_cod(p5)}<span>{h(C[p5]["t"])}</span><span class="mini">NAICS industry (5 digits)</span></li>'
    corpo += f'<li><span class="cod">{c}</span><span>{h(v["t"])}</span><span class="mini">This industry</span></li></ul>'
    vicini = [x for x in sei_di(g4) if x != c]
    if vicini:
        corpo += f'<h2 id="nearby">Other codes in industry group {g4}</h2><ul class="albero">'
        corpo += "".join(f'<li>{link_cod(x)}<span>{h(C[x]["t"])}</span></li>' for x in vicini) + "</ul>"
    corpo += nota(f"Pick the code from the primary activity of the establishment and read the whole description, the cross-references and the "
                  f"index entries: the official examples are not a complete list. Before using it on a form, {FRASE_FISSA}.", "info", "alert")
    corpo += rim.elenco()
    eyebrow = "2022 NAICS · " + ("U.S. national industry" if not unico(p5) else "NAICS industry (6 digits)")
    coda_sic = "the SIC equivalent" if SIC22[c]["diretto"] else ("the SIC crosswalk" if SIC22[c]["righe"] else "the SIC status")
    testata = banda(eyebrow, f"NAICS code {c}: {v['t']}",
                    f"Official 2022 title and description, {num(len(v['idx']))} activities from the Census Bureau index, the NAICS 2017 code and {coda_sic}.",
                    icona="tag")
    coda = f"official 2022 description, {len(v['idx'])} index activities, 2017 code and {coda_sic.replace('the ', '')}."
    pagina(f"{c}/", titolo_pagina(c, "NAICS "), descr_pagina(c, coda), corpo, testata, briciole=briciole_di(c), indicizza=INDICIZZA.get(f"{c}/", True))


def sezione_cinque(c5, rim):
    """Capitolo di un'industria a 5 cifre con più figli, dentro la pagina del gruppo a 4 cifre."""
    v = C[c5]
    out = f'<section class="voce cinque" id="n-{c5}"><h2><span class="chip-cod">{c5}</span>{h(v["t"])}</h2>'
    out += f'<p class="en">NAICS industry (5 digits){" · comparable in Canada and Mexico (T)" if v.get("T") else ""}</p>'
    out += f'<div class="testo">{paragrafi(c5)}</div>{rim.ref("descrizioni")}'
    out += blocco_esempi(c5)
    out += blocco_rimandi(c5)
    out += '<h3>Six-digit U.S. industries</h3><ul class="albero">'
    out += "".join(f'<li>{link_cod(x)}<span>{h(C[x]["t"])}</span><span class="mini">{num(len(C[x]["idx"]))} index entries</span></li>' for x in FIGLI[c5])
    return out + "</ul></section>"


def pagina_gruppo(g):
    rim = Rimandi()
    v = C[g]
    corpo = fatti(g)
    if v["d"]:
        corpo += f'<h2 id="description">Official description</h2><div class="testo">{paragrafi(g)}</div>{rim.ref("descrizioni")}'
    corpo += f'<h2 id="industries">Industries in group {g}</h2>' + albero_figli(g)
    for f in FIGLI[g]:
        if not unico(f):
            corpo += sezione_cinque(f, rim)
    s3 = v["p"]
    altri = [x for x in FIGLI[s3] if x != g]
    if altri:
        corpo += f'<h2 id="nearby">Other industry groups in subsector {s3}</h2><ul class="albero">'
        corpo += "".join(f'<li>{link_cod(x)}<span>{h(C[x]["t"])}</span></li>' for x in altri) + "</ul>"
    corpo += rim.elenco()
    n6 = len(sei_di(g))
    testata = banda("2022 NAICS · Industry group (4 digits)", f"NAICS {g}: {v['t']}",
                    f"{n6} six-digit code{'s' if n6 != 1 else ''} with official titles and descriptions; subsector {s3} «{h(C[s3]['t'])}».", icona="tree")
    coda = f"industry group with {n6} six-digit code{'s' if n6 != 1 else ''}, official descriptions and examples."
    pagina(f"{g}/", titolo_pagina(g, "NAICS "), descr_pagina(g, coda), corpo, testata, briciole=briciole_di(g), indicizza=INDICIZZA.get(f"{g}/", True))


def pagina_sotto(s):
    rim = Rimandi()
    v = C[s]
    corpo = fatti(s)
    if v["d"]:
        corpo += f'<h2 id="description">Official description</h2><div class="testo">{paragrafi(s)}</div>{rim.ref("descrizioni")}'
    corpo += f'<h2 id="groups">Industry groups in subsector {s}</h2>'
    for g in FIGLI[s]:
        corpo += f'<h3 class="cat-h">{link_cod(g)} {h(C[g]["t"])}</h3>' + albero_figli(g, mostra_sei=False)
    corpo += rim.elenco()
    n6 = len(sei_di(s))
    sett = v["p"]
    testata = banda("2022 NAICS · Subsector (3 digits)", f"NAICS {s}: {v['t']}",
                    f"{len(FIGLI[s])} industry groups and {n6} six-digit codes in sector {sett} «{h(C[sett]['t'])}».", icona="tree")
    coda = f"subsector with {len(FIGLI[s])} industry groups and {n6} six-digit codes."
    pagina(f"{s}/", titolo_pagina(s, "NAICS "), descr_pagina(s, coda), corpo, testata, briciole=briciole_di(s), indicizza=INDICIZZA.get(f"{s}/", True))


def pagina_settore(s):
    rim = Rimandi()
    v = C[s]
    corpo = fatti(s)
    if v["d"]:
        corpo += f'<h2 id="description">Official description</h2><div class="testo">{paragrafi(s)}</div>{rim.ref("descrizioni")}'
    corpo += f'<h2 id="subsectors">Subsectors of sector {s}</h2>' + albero_figli(s)
    u = NA["conteggi_ufficiali"][s]
    corpo += (f'<p class="small">Official counts for sector {s}: {u["3"]} subsectors, {u["4"]} industry groups, {u["5"]} NAICS industries, {u["6"]} six-digit '
              f'industries ({u["6_dettaglio_usa"]} with U.S. detail, {u["6_come_5"]} the same as the five-digit industry).{rim.ref("conteggi")}</p>')
    corpo += blocco_guide(s)
    corpo += rim.elenco()
    n6 = len(sei_di(s))
    testata = banda("2022 NAICS · Sector (2 digits)", f"NAICS sector {s}: {v['t']}",
                    f"{len(FIGLI[s])} subsector{'s' if len(FIGLI[s]) != 1 else ''} and {n6} six-digit codes, with the official description of the sector.", icona="tree")
    coda = f"sector with {len(FIGLI[s])} subsectors and {n6} six-digit codes, official description."
    pagina(f"{s}/", titolo_pagina(s, "NAICS Sector "), descr_pagina(s, coda), corpo, testata, briciole=[("Home", ""), (s, f"{s}/")],
           indicizza=INDICIZZA.get(f"{s}/", True))


# ---------------------------------------------------------------- indice di ricerca
GUIDE_RICERCA = [
    ("NAICS 2017 to 2022 conversion", "/naics-2017-to-2022/", "Guide"),
    ("SIC to NAICS conversion table", "/sic-to-naics/", "Guide"),
    ("Ecommerce and online retail: 2017 code 454110 in NAICS 2022", "/naics-2017-to-2022/#v-454110", "Guide"),
    ("NAICS codes by business activity", "/naics-code-for/", "Guide"),
]


def vol_frase(f):
    """Volume mensile misurato di una frase: misura del 13/11 (volumi-attivita-…json), altrimenti quella del 12/11 (volumi.json)."""
    v = VOLA["frasi"].get(f, {}).get("volume")
    if v is not None:
        return v
    return VOL["frasi"].get(f, {}).get("volume") or 0


def volume(a):
    """Volume di una pagina «NAICS code for …»: la frase misurata più cercata (le forme «naics code for X» e «X naics code» sono varianti
    vicine che Google Ads conta insieme: non si sommano)."""
    return max((vol_frase(f) for f in a["frasi"]), default=0)


ATTIVITA = [a for a in ATT if volume(a) >= MIN_VOLUME_ATTIVITA]


def indice_ricerca():
    voci = [["Guide", t, u, "p", n] for t, u, n in GUIDE_RICERCA]
    voci += [["Guide", a["h1"][0].upper() + a["h1"][1:], f"/{a['slug']}/", "p", "Guide"] for a in ATTIVITA]
    for c in ORDINE:
        if C[c]["l"] == 5 and unico(c):
            continue  # stessa pagina e stesso titolo del figlio a 6 cifre: lo trova già la ricerca per cifre
        voci.append([c, C[c]["t"], url_di(c), str(C[c]["l"]), ""])
    for c17 in N17:
        if c17 in N17_STESSI:
            continue
        voci.append([c17, T17[c17], f"/naics-2017-to-2022/#v-{c17}", "17", "2017 → " + ", ".join(A22[c17][:3])])
    for s, v in sorted(SIC.items()):
        voci.append([s, v["t"], f"/sic-to-naics/#sic-{s}", "sic", "SIC 1987"])
    frasi = {c: "|".join(C[c]["idx"]) for c in SEI if C[c]["idx"]}
    return (json.dumps(voci, ensure_ascii=False, separators=(",", ":")), json.dumps(frasi, ensure_ascii=False, separators=(",", ":")))


INDICE, FRASI = indice_ricerca()
INDICE_FILE = f"index.{_impronta(INDICE)}.json"
FRASI_FILE = f"entries.{_impronta(FRASI)}.json"


# ---------------------------------------------------------------- home
def home():
    rim = Rimandi()
    form = (f'<form class="cerca" role="search" id="search" action="/" onsubmit="return false"><label for="q" hidden>Search a NAICS code</label>'
            f'<input id="q" type="search" data-cerca data-indice="/assets/{INDICE_FILE}" data-frasi="/assets/{FRASI_FILE}" '
            'placeholder="Activity or code: bakery, software, 5415…" autocomplete="off"></form>'
            '<ul class="risultati" data-risultati hidden></ul>')
    testata = banda("NAICS 2022 · official Census Bureau files", "Find your NAICS code",
                    f"Search by activity, by code, with an <strong>old 2017 code</strong> or a <strong>SIC code</strong>: official title, description, "
                    f"the {NUM['n_idx']} activities of the official index and the SIC equivalents.", form, icona="search")
    corpo = (f'<div class="card pull cifre"><div class="cifra main"><b>{NUM["n_6"]}</b><span>six-digit NAICS 2022 industries, one page each</span></div>'
             f'<div class="cifra"><b>{NUM["n_idx"]}</b><span>activities in the official index</span></div>'
             f'<div class="cifra"><b>{NUM["n17"]}</b><span>NAICS 2017 codes with the 2022 code</span></div>'
             f'<div class="cifra"><b>{NUM["n_sic"]}</b><span>1987 SIC codes linked to NAICS</span></div>'
             f'<p class="asof">{ico("check")}NAICS 2022 files of the U.S. Census Bureau, read on {data_lunga(CONTROLLO)}; counts checked against '
             f'the official summary table.{rim.ref("conteggi")}</p></div>')
    corpo += '<h2 id="guides">Guides</h2><ul class="griglia">'
    utili = [("/naics-2017-to-2022/", "NAICS 2017 to 2022", f"The 2022 code for each of the {NUM['n17']} six-digit 2017 codes."),
             ("/sic-to-naics/", "SIC to NAICS", f"The NAICS codes linked to each of the {NUM['n_sic']} SIC codes of 1987.")]
    utili += [(f"/{a['slug']}/", maiuscola(a["h1"]), accorcia(a["descrizione"], 90))
              for a in sorted(ATTIVITA, key=lambda a: (-volume(a), a["slug"]))[:7]]
    utili.append(("/naics-code-for/", "NAICS codes by business activity", f"All {len(ATTIVITA)} guides, from restaurants and trucking to software."))
    corpo += "".join(f'<li><a href="{u}"><b>{h(t)}</b><span>{h(s)}</span></a></li>' for u, t, s in utili) + "</ul>"
    corpo += f'<h2 id="sectors">The {len(SETTORI)} NAICS sectors</h2><ul class="albero">'
    for s in SETTORI:
        corpo += (f'<li><a class="cod" href="{url_di(s)}" aria-label="Sector {s}">{s}</a><span>{h(C[s]["t"])}</span>'
                  f'<span class="mini">{num(len(sei_di(s)))} six-digit codes</span></li>')
    corpo += "</ul>"
    corpo += ('<h2 id="how-to-read">How to read a NAICS code</h2><div class="testo">'
              f'<p>NAICS uses a six-digit code. The first two digits are the sector, the third the subsector, the fourth the industry group, the fifth '
              f'the NAICS industry and the sixth the national industry; a zero as the sixth digit generally means the NAICS industry and the U.S. '
              f'industry are the same.{rim.ref("manuale")} Example with {link_cod("541511")} «{h(C["541511"]["t"])}»:</p><ul>'
              f'<li><strong>54</strong>: sector «{h(C["54"]["t"])}»</li><li><strong>541</strong>: subsector «{h(C["541"]["t"])}»</li>'
              f'<li><strong>5415</strong>: industry group «{h(C["5415"]["t"])}»</li><li><strong>54151</strong>: NAICS industry «{h(C["54151"]["t"])}»</li>'
              f'<li><strong>541511</strong>: U.S. industry, the six-digit code used on forms.</li></ul>'
              '<p>Each industry has an official description, often with illustrative examples and cross-references to the codes where related activities '
              'are classified. The official index adds thousands of specific activities, each pointing to one six-digit code.</p></div>')
    voci = faq_pagina("home", rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/", "inLanguage": "en-US"}]
    if f_ld:
        ld.append(f_ld)
    pagina("", "NAICS Code Lookup: search 2022 NAICS codes and SIC codes",
           "Search NAICS 2022 codes by activity or number: official Census titles and descriptions, 20,000 index activities, 2017 codes and SIC equivalents.",
           corpo, testata.replace("{bc}", ""), jsonld=ld)


# ---------------------------------------------------------------- tabelle 2017 → 2022 e SIC → NAICS
def filtro(placeholder, tab, nome):
    return (f'<div data-tabella><div class="filtri"><input type="search" data-filtro placeholder="{h(placeholder)}" aria-label="Filter the {nome}"></div>'
            f'<p class="conteggio" data-conteggio></p>{tab}<p class="vuoto-ricerca" data-vuoto hidden>No code found.</p>'
            '<p class="altre" data-altre hidden><button type="button" class="btn sec" data-altre-piu>Show 100 more</button>'
            '<button type="button" class="btn sec" data-altre-tutte>Show all</button></p></div>')


def da_2017():
    rim = Rimandi()
    righe, attr = [], []
    for c17 in N17:
        nuovi = A22[c17]
        if c17 in N17_STESSI:
            stato = '<span class="tag neu">same</span>'
        elif len(nuovi) > 1:
            stato = f'<span class="tag car">split in {len(nuovi)}</span>'
        elif nuovi[0] != c17:
            stato = '<span class="tag car">renumbered</span>' if len(DA17[nuovi[0]]) == 1 else '<span class="tag car">merged</span>'
        else:
            stato = '<span class="tag car">content changed</span>'
        dest = "<br>".join(f'{link_cod(x)} {h(C[x]["t"])}' for x in nuovi)
        righe.append([f'<span class="cod">{c17}</span>', h(T17[c17]), dest, stato])
        attr.append(f' id="v-{c17}"')
    tab = tabella(["NAICS 2017", "2017 title", "NAICS 2022", "Change"], righe, attr=attr, resp="resp7")
    corpo = (f'<div class="card pull"><p style="margin:0"><strong>For each six-digit NAICS 2017 code: the NAICS 2022 code or codes that contain it</strong>, '
             f'from the Census Bureau\'s full 2017 → 2022 concordance.{rim.ref("c17_22")} {NUM["n17_stessi"]} of the {NUM["n17"]} codes are unchanged; '
             f'the others were renumbered, split, merged or changed in content.</p></div>')
    corpo += filtro("Old code or word: 454110, electronic shopping…", tab, "2017 codes")
    nuovi_sett = Counter(antenato(c, 2) for c in SEI6_NUOVI)
    rr = [[link_cod(s), h(C[s]["t"]), num(n)] for s, n in nuovi_sett.most_common()]
    corpo += (f'<h2 id="new-codes">New six-digit codes in 2022, by sector</h2><p class="small">Codes marked «new code for 2022 NAICS» in the official '
              f'2022 structure.{rim.ref("struttura")}</p>' + tabella(["Sector", "Title", "New codes"], rr, num_=[2]))
    split = sorted((c for c in N17 if len(A22[c]) > 1), key=lambda c: -len(A22[c]))[:8]
    corpo += ('<h2 id="most-split">The 2017 codes split the most</h2><ul class="albero">'
              + "".join(f'<li><a class="cod" href="#v-{c}">{c}</a><span>{h(T17[c])}</span><span class="mini">{len(A22[c])} codes in 2022</span></li>' for c in split)
              + "</ul>")
    voci = faq_pagina("naics-2017-to-2022", rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    testata = banda("Conversion table", "NAICS 2017 to NAICS 2022: the new code",
                    f"Type an old code or a word: {NUM['n17']} six-digit 2017 codes with the 2022 code from the official Census concordance.", icona="swap")
    pagina("naics-2017-to-2022/", "NAICS 2017 to 2022 conversion: every old code",
           f"The NAICS 2022 code for each of the {NUM['n17']} six-digit 2017 codes, from the official Census Bureau concordance: renumbered, split and merged codes.",
           corpo, testata, briciole=[("Home", ""), ("NAICS 2017 to 2022", "naics-2017-to-2022/")], jsonld=[f_ld] if f_ld else None)


def sic_naics():
    rim = Rimandi()
    righe, attr = [], []
    for s, v in sorted(SIC.items()):
        parti = []
        for x in v["n97"]:
            t97 = re.sub(r"\s*\(pt\)\s*$", "", x["t97"]).strip().lower()
            stessi = [y for y in x["n22"] if C[y]["t"].lower() == t97]
            if stessi and len(x["n22"]) > len(stessi):
                arrivo = (", ".join(link_cod(y) for y in stessi) + ' <span class="mini">(same title)</span>; pieces also in '
                          + ", ".join(link_cod(y) for y in x["n22"] if y not in stessi))
            else:
                arrivo = ", ".join(link_cod(y) for y in x["n22"]) if x["n22"] else '<span class="mini">no single code</span>'
            pezzo = f'<b>{h(x["parte"])}</b>: ' if x["parte"] else ""
            n97 = x["n"] if re.fullmatch(r"\d{6}", x["n"]) else x["n"]
            parti.append(f'<li>{pezzo}1997 <span class="cod">{h(n97)}</span> {h(x["t97"])} → 2022 {arrivo}</li>')
        cella = f'<ul class="chips-cod" style="display:block">{"".join(parti)}</ul>' if parti else '<span class="mini">not in the concordance</span>'
        if len(parti) > 3:
            cella = f'<details class="tutte"><summary>{len(parti)} parts</summary>{cella}</details>'
        righe.append([f'<span class="cod">{s}</span>', h(v["t"]), cella])
        attr.append(f' id="sic-{s}"')
    tab = tabella(["SIC 1987", "SIC title", "1997 NAICS (official) → 2022 NAICS"], righe, attr=attr, resp="resp7")
    corpo = (f'<div class="card pull"><p style="margin:0"><strong>For each four-digit 1987 SIC code: the 1997 NAICS codes of the official Census '
             f'concordance</strong>, part by part, and the 2022 codes reached by following the official concordances 1997 → 2002 → 2007 → 2012 → 2017 → 2022.'
             f'{rim.ref(["sic_naics97", "c97_02", "c02_07", "c07_12", "c12_17", "c17_22"])}</p></div>')
    corpo += nota("The only official SIC ↔ NAICS concordance of the Census Bureau is between 1987 SIC and 1997 NAICS. The step from 1997 to 2022 is "
                  "our chaining of the later official concordances: when a NAICS industry was split or merged after 1997, a SIC code can lead to "
                  "several 2022 codes, and some of them hold only a small piece of the old SIC industry. When one of the 2022 codes kept the 1997 "
                  f"title it is listed first. Read the descriptions and {FRASE_FISSA}.", "info")
    corpo += filtro("SIC code or word: 7371, consulting…", tab, "SIC codes")
    voci = faq_pagina("sic-to-naics", rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    testata = banda("Crosswalk", "SIC to NAICS: the NAICS code for every SIC code",
                    f"Type a SIC code or a word: {NUM['n_sic']} SIC codes of 1987 with the official 1997 NAICS codes and the 2022 codes they lead to.", icona="swap")
    pagina("sic-to-naics/", "SIC to NAICS crosswalk: 1987 SIC codes to NAICS 2022",
           f"SIC to NAICS conversion: {NUM['n_sic']} SIC codes with the official Census 1987 SIC to 1997 NAICS concordance and the NAICS 2022 codes they lead to.",
           corpo, testata, briciole=[("Home", ""), ("SIC to NAICS", "sic-to-naics/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- pagine «NAICS code for …»
def maiuscola(t):
    return t[0].upper() + t[1:]


def vi(c, e):
    """Voce dell'indice ufficiale citata tale e quale, con il codice a cui l'indice la assegna (verifica.py la ricontrolla sul file grezzo)."""
    if e not in C[c]["idx"]:
        raise SystemExit(f"voce «{e}» assente dall'indice ufficiale di {c}")
    return f'<q class="vi" data-c="{c}">{h(e)}</q>'


def voci_attivita(a):
    """{codice a 6 cifre: voci dell'indice che corrispondono alla regex della pagina}, solo nei codici dei prefissi indicati."""
    gruppi = defaultdict(list)
    if not a.get("regex"):
        return gruppi
    rx = re.compile(a["regex"], re.I)
    pref = a.get("prefissi")
    for c in SEI:
        if pref and not any(c.startswith(p) for p in pref):
            continue
        for e in C[c]["idx"]:
            if rx.search(e):
                gruppi[c].append(e)
    return gruppi


def scelte_attivita(a, gruppi):
    """Righe della tabella delle scelte: per ogni codice in evidenza, le voci dell'indice che lo indicano (scelte a mano o le prime trovate)."""
    out = {}
    for c in a["evidenza"]:
        if c not in C or C[c]["l"] != 6:
            raise SystemExit(f"{a['slug']}: {c} non è un codice a 6 cifre del 2022")
        voci = a.get("scelte", {}).get(c) or gruppi.get(c, [])[:3]
        if not voci:
            raise SystemExit(f"{a['slug']}: nessuna voce dell'indice ufficiale per {c}")
        out[c] = voci
    return out


def esempi_sottosettore(s3, n=2):
    """I codici a 6 cifre del sottosettore con più voci nell'indice (esempi nella pagina attività di un settore)."""
    return sorted((x for x in sei_di(s3) if C[x]["idx"]), key=lambda x: (-len(C[x]["idx"]), x))[:n]


def blocco_settore(s):
    sei = sei_di(s)
    if len(sei) <= SOGLIA_SETTORE_COMPLETO:
        out = f'<h2 id="sector">All {len(sei)} six-digit codes of sector {s}</h2>'
        for s3 in FIGLI[s]:
            rr = [[link_cod(x), h(C[x]["t"]), vi(x, C[x]["idx"][0]) if C[x]["idx"] else "—"] for x in sei_di(s3)]
            out += f'<h3 class="cat-h">{link_cod(s3)} {h(C[s3]["t"])}</h3>'
            out += tabella(["Code", "Official title", "First entry of the official index"], rr, resp="resp7")
        return out
    rr = []
    for s3 in FIGLI[s]:
        es = "; ".join(f'{link_cod(x)} {vi(x, C[x]["idx"][0])}' for x in esempi_sottosettore(s3))
        rr.append([link_cod(s3), h(C[s3]["t"]), num(len(sei_di(s3))), es])
    return (f'<h2 id="sector">The {len(FIGLI[s])} subsectors of sector {s}</h2><p class="small">For each subsector, the number of six-digit '
            'industries and the two with the most entries in the official index, each with its first entry.</p>'
            + tabella(["Subsector", "Official title", "Six-digit codes", "Examples from the official index"], rr, num_=[2], resp="resp7"))


def link_2017(t):
    """Codici a 6 cifre del 2017 che non esistono nel 2022 (es. 454110): link alla riga della tabella 2017 → 2022."""
    return re.sub(r"(?<![\w/#>-])(\d{6})(?![\w<-])",
                  lambda m: f'<a class="cod" href="/naics-2017-to-2022/#v-{m.group(1)}">{m.group(1)}</a>' if m.group(1) not in C and m.group(1) in T17 else m.group(1), t)


def pagina_attivita(a):
    rim = Rimandi()
    gruppi = voci_attivita(a)
    scelte = scelte_attivita(a, gruppi)
    ordinati = sorted(gruppi, key=lambda c: (-len(gruppi[c]), c))
    extra = {"n_voci": num(sum(len(v) for v in gruppi.values())), "n_codici": num(len(gruppi))}
    s = a.get("settore")
    if s:
        extra[f"n_sei_{s}"] = num(len(sei_di(s)))
        extra["n_sei_settore"] = num(len(sei_di(s)))
        extra["n_sotto_settore"] = num(len(FIGLI[s]))
    intro = riempi(a["intro"], extra)
    corpo = f'<div class="card pull"><p style="margin:0">{link_2017(h(intro))}{rim.ref(["indice", "codici"])}</p></div>'
    if scelte:
        rr = [["; ".join(vi(c, e) for e in voci), link_cod(c), h(C[c]["t"])] for c, voci in scelte.items()]
        corpo += ('<h2 id="which-code">Which code: what the official index says</h2><p class="small">If the main activity of the establishment is '
                  f'one of the entries in the first column, the official 2022 index points to the code next to it. Entries are quoted word for word.'
                  f'{rim.ref("indice")}</p>' + tabella(["Official index entries", "NAICS 2022 code", "Official title"], rr, resp="resp7"))
    for cod, n in a.get("citazioni", []):
        corpo += (f'<blockquote class="legge">{h(C[cod]["d"][n])}<cite>Official description of {link_cod(cod)} «{h(C[cod]["t"])}», '
                  f'2022 NAICS{rim.ref("descrizioni")}</cite></blockquote>')
    if scelte:
        corpo += '<h2 id="main-codes">The codes to look at first</h2>'
    for c in scelte:
        v = C[c]
        prima = v["d"][0] if v["d"] and [c, 0] not in a.get("citazioni", []) else ""  # già citata sopra: non si ripete
        corpo += (f'<section class="voce" id="c-{c}"><h3><span class="chip-cod">{c}</span><a href="{url_di(c)}">{h(v["t"])}</a></h3>'
                  + (f'<div class="testo"><p>{h(prima)}</p></div>' if prima else '<p class="small">Official description quoted above.</p>'))
        voci = list(dict.fromkeys(scelte[c] + gruppi.get(c, [])))
        corpo += f'<p class="small">In the official index: {"; ".join(vi(c, e) for e in voci[:6])}{"…" if len(voci) > 6 else ""}</p>'
        princ, altre, _ = sic_righe(c)
        sics = sorted({x["sic"] for x in (princ or altre)})
        if sics:
            corpo += (f'<p class="small">SIC 1987{"" if princ else " (partial match)"}: '
                      + ", ".join(f'<a class="cod" href="/sic-to-naics/#sic-{x}">{x}</a>' for x in sics[:6]) + "</p>")
        corpo += "</section>"
    if scelte:
        corpo += f'<p class="small">Descriptions: 2022 NAICS, U.S. Census Bureau.{rim.ref("descrizioni")}</p>'
    if s:
        corpo += blocco_settore(s)
    if gruppi:
        rr = [[link_cod(c), h(C[c]["t"]) + f'<small>{"; ".join(vi(c, e) for e in gruppi[c][:4])}{"…" if len(gruppi[c]) > 4 else ""}</small>',
               num(len(gruppi[c]))] for c in ordinati]
        corpo += (f'<h2 id="index">Every matching entry of the official index, by code</h2><p class="small">{num(sum(len(v) for v in gruppi.values()))} '
                  f'entries of the 2022 NAICS index match this guide ({h(a["nome"])}); here they are grouped by six-digit code, and the full list of each code is on its page.'
                  f'{rim.ref("indice")}</p>' + tabella(["Code", "Title and entries", "Entries"], rr, num_=[2], resp="resp7"))
    corpo += nota(f"The code follows the primary activity of the establishment, not a keyword: read the description of each candidate code. "
                  f"Before using a code on a form, {FRASE_FISSA}.", "info", "alert")
    voci = faq_pagina(a["slug"], rim, extra)
    f_html, f_ld = faq_html(voci)
    corpo += f_html
    corpo += ('<p class="small">More activities: <a href="/naics-code-for/">NAICS codes by business activity</a>.</p>' + rim.elenco())
    controlla_codici_attivita(a["slug"], corpo)
    testata = banda("NAICS code by activity", maiuscola(a["h1"]), h(a["descrizione"]), icona="tag")
    pagina(a["slug"] + "/", a["titolo"], a["descrizione"], corpo, testata,
           briciole=[("Home", ""), ("By activity", "naics-code-for/"), (maiuscola(a["h1"]), a["slug"] + "/")], jsonld=[f_ld] if f_ld else None,
           indicizza=INDICIZZA_ATT.get(a["slug"] + "/", True))


def controlla_codici_attivita(dove, corpo):
    """Ogni codice a 6 cifre mostrato (link o numero nel testo) deve avere nella pagina almeno una voce dell'indice ufficiale citata;
    i soli numeri ammessi senza voce sono codici 2017 che non esistono più, con il link alla tabella 2017 → 2022."""
    t = re.sub(r'<section class="fonti-box".*?</section>', " ", corpo, flags=re.S)
    citati = set(re.findall(r'<q class="vi" data-c="(\d{6})">', t))
    mostrati = set(re.findall(r'href="/(\d{6})/"', t)) | set(re.findall(r"(?<![\d#/-])(\d{6})(?!\d)", unescape(re.sub(r"<[^>]+>", " ", t))))
    senza = [c for c in sorted(mostrati - citati) if c in C]
    if senza:
        raise SystemExit(f"{dove}: codici mostrati senza una voce dell'indice ufficiale citata nella pagina: {', '.join(senza)}")
    for c in sorted(mostrati - citati):
        if c not in T17 or f'href="/naics-2017-to-2022/#v-{c}"' not in t:
            raise SystemExit(f"{dove}: {c} non è un codice NAICS 2022 (né un codice 2017 con il suo link)")


GUIDE_DI = defaultdict(list)  # codice -> pagine «NAICS code for …» che lo indicano
for _a in ATTIVITA:
    for _c in _a["evidenza"]:
        GUIDE_DI[_c].append(_a)
    if _a.get("settore"):
        GUIDE_DI[_a["settore"]].append(_a)


def blocco_guide(c):
    """Link dalle pagine di codice alle guide per attività che le citano (ripreso: non conta come testo proprio nella misura)."""
    if not GUIDE_DI.get(c):
        return ""
    return ('<section data-ripreso><h2 id="guides">Guides by activity that point to this code</h2><ul>'
            + "".join(f'<li><a href="/{a["slug"]}/">{h(maiuscola(a["h1"]))}</a></li>' for a in GUIDE_DI[c]) + "</ul></section>")


def indice_attivita():
    rim = Rimandi()
    righe = []
    for a in sorted(ATTIVITA, key=lambda a: a["nome"].lower()):
        gruppi = voci_attivita(a)
        scelte = scelte_attivita(a, gruppi)
        if scelte:
            c = next(iter(scelte))
            cod = f'{link_cod(c)} {vi(c, scelte[c][0])}'
            if len(scelte) > 1:
                cod += f'<small>and {len(scelte) - 1} other code{"s" if len(scelte) > 2 else ""} compared in the guide</small>'
        else:
            cod = f'Sector {link_cod(a["settore"])}'
        righe.append([f'<a href="/{a["slug"]}/">{h(maiuscola(a["nome"]))}</a>', cod])
    corpo = ('<div class="card pull"><p style="margin:0">Guides for the activities people search most often with «NAICS code for …» '
             f'({len(ATTIVITA)} activities, each with at least {MIN_VOLUME_ATTIVITA} searches a month in the United States). Each guide quotes the '
             f'entries of the official 2022 index that point to each code and links to the code pages.{rim.ref("indice")}</p></div>')
    corpo += ('<h2 id="activities">Activities and their codes</h2><p class="small">First column: the guide. Second column: the first code of the guide, '
              'with an entry of the official index that points to it, and how many other codes the guide compares.</p>'
              + tabella(["Activity", "Codes from the official index"], righe, resp="resp7"))
    corpo += ('<h2 id="other">Activity not listed?</h2><div class="testo"><p>Use the <a href="/#search">search on the home page</a>: it covers all '
              f'{NUM["n_idx"]} entries of the official index. The NAICS manual says to identify the primary business activity first and then read '
              f'the full description of the industry, including cross-references and illustrative examples.{rim.ref("manuale")}</p></div>')
    corpo += nota(f"These guides give the codes of the official classification, not advice: {FRASE_FISSA}.", "info", "alert")
    corpo += rim.elenco()
    controlla_codici_attivita("naics-code-for", corpo)
    testata = banda("NAICS code by activity", "NAICS codes by business activity",
                    f"{len(ATTIVITA)} guides to the activities people search for, from restaurants and trucking to software and real estate.",
                    corta=True, icona="tag")
    pagina("naics-code-for/", f"NAICS Codes by Business Activity: {len(ATTIVITA)} Guides",
           f"NAICS codes for {len(ATTIVITA)} common business activities, from restaurants and trucking to real estate and software, with official index entries.",
           corpo, testata, briciole=[("Home", ""), ("By activity", "naics-code-for/")])


# ---------------------------------------------------------------- pagine del sito
MODULO = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card" data-correzioni>
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or code<input type="text" name="page" required maxlength="300" placeholder="For example /541511/ or 541511"></label>
<label>What does not match the official files?<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<p class="small">Please do not include your name, email address or other personal details: the form does not ask for them and we do not reply to messages.</p>
<p class="errore" data-errore hidden>The message was not sent. Please try again.</p>
<button type="submit" class="btn">Send correction</button>
</form>
<p class="ok" data-ok hidden><strong>Thank you.</strong> We will check it against the official files.</p>"""


def come_controlliamo(n_idx, n_noidx):
    rim = Rimandi()
    corpo = ('<div class="card pull"><p style="margin:0"><strong>We use only the official files of the U.S. Census Bureau, with their date and fingerprint.</strong> '
             f'Titles, descriptions, index entries and cross-references are shown as published. We do not tell you which code to choose: {FRASE_FISSA}.</p></div>')
    corpo += '<h2 id="files">The files we use</h2>'
    rr = [[f'<a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a>{rim.ref(fid)}', data_lunga(f["letto_il"]), num(f["byte"]), f'<code>{f["sha256"][:12]}</code>']
          for fid, f in FJ["file"].items()]
    corpo += tabella(["File", "Read on", "Bytes", "Fingerprint"], rr, num_=[2],
                     caption="The fingerprint (SHA-256, first 12 characters) identifies the file we read: when it changes, we run every check again.")
    u = NA["conteggi_ufficiali"]["Totale"]
    corpo += '<h2 id="method">What we do with the data</h2><div class="testo"><ol>'
    corpo += (f'<li><strong>Tree.</strong> {NUM["n_codici"]} codes from the 2–6 digit file, each with its parent (2 → 3 → 4 → 5 → 6 digits); the build stops if a code '
              f'is missing, doubled or without the right parent, and if the counts differ from the official summary table ({len(SETTORI)} sectors, {u["3"]} '
              f'subsectors, {u["4"]} industry groups, {u["5"]} NAICS industries, {u["6"]} six-digit industries).</li>'
              f'<li><strong>Descriptions and index.</strong> Descriptions, illustrative examples, cross-references and the {NUM["n_idx"]} index entries are '
              'shown word for word; codes cited in the texts become links.</li>'
              '<li><strong>2017 codes.</strong> From the official 2022 ↔ 2017 concordance, with the change indicators of the 2022 structure.</li>'
              '<li><strong>SIC codes.</strong> The Census Bureau publishes one official SIC ↔ NAICS concordance, between 1987 SIC and 1997 NAICS. To reach 2022 '
              'we follow the official concordances 1997 → 2002 → 2007 → 2012 → 2017 → 2022. When the 2022 industry has the same code and content since 1997 the '
              'official line applies as it is; otherwise the page says the link is our chaining and that a SIC code may cover only a piece of the industry.</li>'
              '</ol></div>')
    corpo += ('<h2 id="pages">Which pages we publish</h2><div class="testo">'
              f'<p>One page for each sector ({NUM["n_2"]}), subsector ({NUM["n_3"]}), industry group ({NUM["n_4"]}) and six-digit industry ({NUM["n_6"]}). '
              f'Five-digit NAICS industries do not get their own page: when they have a single six-digit industry (code ending in 0, same title, same '
              'description) the six-digit page covers both; when they have several, they are a section of the industry group page, with their own address '
              f'(#n- and the code). We ask search engines to index {n_idx} code pages, those with at least {MIN_PAROLE_PROPRIE} groups of words of their '
              f'own and less than {int(MAX_SOVRAPPOSIZIONE * 100)}% of text in common with the most similar page, plus the shorter six-digit pages that people '
              f'search for (the code or its activity appears in the search suggestions we saved); the other {n_noidx} stay available but '
              'are not indexed and carry no ads. «NAICS code for …» pages exist only for activities with at least '
              f'{MIN_VOLUME_ATTIVITA} measured Google searches a month in the United States; they quote only entries of the official index and '
              'official descriptions, and follow a stricter rule of own text: the quoted official texts count as text in common with the code pages, the quoted '
              f'index entries are not counted as text of the page, and less than {int(MAX_SOVRAPPOSIZIONE_ATTIVITA * 100)}% may be in common with the most similar page.</p></div>')
    corpo += ('<h2 id="updates">How often we update</h2><div class="testo"><p>Every month we download the Census files again: if a fingerprint changes we '
              'run all the checks. NAICS is revised every five years; when a new edition is published, the site moves to it.</p></div>')
    corpo += ('<h2 id="corrections">Report an error</h2><p>Found a difference with the official files? Tell us the page and, if you can, the link to the '
              'official source. The form does not ask who you are.</p>' + MODULO)
    corpo += rim.elenco()
    testata = banda("How we check", "How we read and check the Census files",
                    "Which files we use, when we read them, what we derive, which pages we index and how often we update.", corta=True, icona="shield")
    pagina("how-we-check/", "How we check: Census NAICS files, checks and updates",
           "How NAICS Code Lookup uses the Census Bureau NAICS 2022 files and concordances: file fingerprints, tree and count checks, SIC chaining.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")])


def about():
    corpo = ('<div class="card pull testo"><p><strong>NAICS Code Lookup is an independent, free information site.</strong> It puts the North American '
             'Industry Classification System of the United States into readable pages, with the official descriptions, the activities of the official '
             'index, the old 2017 codes and the 1987 SIC codes.</p></div>'
             '<h2>Why it exists</h2><div class="testo"><p>The official files are spreadsheets with thousands of rows: structure, descriptions, index, '
             'cross-references and concordances are in separate files. Here they are joined code by code, with the source next to each block.</p></div>'
             '<h2>What we are not</h2><div class="testo"><ul><li>We are not the Census Bureau, OMB, the IRS or the SBA, and we are not affiliated with them.</li>'
             f'<li>We give no legal, tax or business advice: {FRASE_FISSA}.</li><li>We do not ask readers for personal data: the form to report an error has no name or '
             'email field.</li></ul></div>'
             '<h2>How the site is paid for</h2><div class="testo"><p>The site may show Google AdSense ads on the pages with the most content. Ads never change '
             'a code or a text, and nobody pays to appear.</p><p>NAICS Code Lookup is part of a small network of free information sites run by the same '
             'independent publisher. How we check the data: <a href="/how-we-check/">how we check</a>.</p></div>')
    testata = banda("About", "About NAICS Code Lookup", "An independent site that makes the NAICS classification readable.", corta=True, icona="people")
    pagina("about/", "About | NAICS Code Lookup",
           "NAICS Code Lookup is an independent, free site, not affiliated with the Census Bureau, with official NAICS 2022 codes, index entries and SIC codes.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")])


def privacy():
    cookie = MON.privacy_cookie("en", SITO_ID, False) or ("<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. "
                                                         "This site does not use profiling cookies and shows no advertising.</p>")
    cal = MON.frase_california(SITO_ID) or "California residents: we do not sell or share personal information."
    corpo = ('<div class="card pull testo"><p>This page explains what NAICS Code Lookup collects. In short: very little.</p></div>'
             '<div class="testo"><h2>The search</h2><p>The code search on the home page and the filters of the tables run in your browser: the words you type '
             'are not sent to us or stored. The site remembers only your choice of light or dark theme in your browser (local storage).</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             '<h2 id="corrections">Corrections form</h2><p>The <a href="/how-we-check/#corrections">form to report an error</a> asks for the page, your '
             'message and, if you wish, a link to the official source. It does not ask for your name or email address, and we ask you not to put personal '
             'details in the message. The form is processed by Netlify Forms on our behalf. We use what you send only to check the page against the official '
             'files and delete it once that is done. There are no accounts, newsletters or comments on this site.</p>'
             f'<h2>Your rights</h2><p>We hold no personal data about readers. If you put personal details in a correction by mistake, send another message '
             f'through the same form and we will delete it. {cal}</p>'
             f'<h2>Changes</h2><p>We update this page when the site changes. Last update: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID, False) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", "Privacy | NAICS Code Lookup",
           "Privacy at NAICS Code Lookup: the search runs in your browser, a cookie-free visit counter, and Google AdSense ads only with consent where required.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = ('<div class="card pull"><p>The page you asked for does not exist. Go back to the <a href="/#search">code search</a>, the '
             '<a href="/#sectors">list of sectors</a> or the <a href="/naics-2017-to-2022/">2017 to 2022 table</a>.</p></div>')
    testata = banda("Error 404", "Page not found", "This address has no page.", corta=True, icona="alert")
    pagina("", "Page not found | NAICS Code Lookup", "Page not found.", corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{CONTROLLO.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in naics/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = naics/sito, Build command vuoto, Publish directory = "."
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
    (SITO / "assets" / INDICE_FILE).write_text(INDICE, encoding="utf-8")
    (SITO / "assets" / FRASI_FILE).write_text(FRASI, encoding="utf-8")


# ---------------------------------------------------------------- indicizzazione delle pagine di codice
def gruppi_di_parole(html_, n=5, voci_a_parte=False):
    """voci_a_parte (pagine attività, revisione del 13/11 sera): ogni voce dell'indice citata (<q class="vi">) è tolta e spezza il testo,
    così gli accostamenti di voci ufficiali diverse nella stessa riga non contano come testo proprio; conta solo la prosa nostra."""
    t = re.sub(r"<section data-ripreso>.*?</section>", " ", html_, flags=re.S)
    t = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", t, flags=re.S | re.I)
    if voci_a_parte:
        t = re.sub(r'<q class="vi"[^>]*>.*?</q>', " \x00 ", t, flags=re.S)
    out = set()
    for pezzo in unescape(re.sub(r"<[^>]+>", " ", t)).lower().split("\x00"):
        w = re.findall(r"\w+", pezzo)
        out |= {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}
    return out


def pagine_codice():
    for s in SETTORI:
        pagina_settore(s)
    for s in SOTTO:
        pagina_sotto(s)
    for g in GRUPPI:
        pagina_gruppo(g)
    for c in SEI:
        pagina_sei(c)


MISURA = {}


def misura():
    global _PROVA
    _PROVA = {}
    pagine_codice()
    testi, _PROVA = _PROVA, None
    ins = {p: gruppi_di_parole(t) for p, t in testi.items()}
    conta = Counter(g for s in ins.values() for g in s)
    GREZZI_CODICE.update(ins)
    # frasi di modello (presenti in almeno QUOTA_MODELLO delle pagine di codice: titoli dei blocchi, avvertenze, spiegazioni fisse)
    # non sono contenuto di nessuna pagina: si tolgono prima di misurare la sovrapposizione
    soglia = QUOTA_MODELLO * len(ins)
    ins = {p: {g for g in s if conta[g] < soglia} for p, s in ins.items()}
    indice = defaultdict(list)
    for p, s in ins.items():
        for g in s:
            if conta[g] <= 40:
                indice[g].append(p)
    for p, a in ins.items():
        proprie = sum(1 for g in a if conta[g] == 1)
        cand = Counter(q for g in a if conta[g] <= 40 for q in indice[g] if q != p)
        meglio = (0.0, "")
        for q, _ in cand.most_common(25):
            c = len(a & ins[q]) / len(a) if a else 0
            if c > meglio[0]:
                meglio = (c, q)
        MISURA[p] = {"proprie": proprie, "sovrapposizione": round(meglio[0], 3), "piu_simile": meglio[1]}
        INDICIZZA[p] = proprie >= MIN_PAROLE_PROPRIE and meglio[0] < MAX_SOVRAPPOSIZIONE
        cod = p.rstrip("/")
        if not INDICIZZA[p] and cod in RICHIESTI and proprie >= MIN_PROPRIE_RICHIESTA and meglio[0] < MAX_SOVRAPPOSIZIONE_RICHIESTA:
            INDICIZZA[p] = True  # pagina corta ma cercata: la descrizione ufficiale è la risposta
            MISURA[p]["richiesta"] = RICHIESTI[cod]


GREZZI_CODICE = {}  # pagina di codice -> gruppi di 5 parole (con le frasi di modello)
MISURA_ATT = {}


def misura_attivita():
    """Pagine «NAICS code for …»: indicizzate solo con almeno MIN_PAROLE_PROPRIE gruppi di 5 parole che non sono in nessun'altra pagina
    (di codice o di attività) e meno di MAX_SOVRAPPOSIZIONE_ATTIVITA di testo in comune con la pagina più simile. Le voci dell'indice e le
    descrizioni ufficiali citate sono anche nelle pagine dei codici: contano solo come testo in comune."""
    global _PROVA
    _PROVA = {}
    for a in ATTIVITA:
        pagina_attivita(a)
    testi, _PROVA = _PROVA, None
    att = {p: gruppi_di_parole(t, voci_a_parte=True) for p, t in testi.items()}
    conta_cod = Counter(g for s in GREZZI_CODICE.values() for g in s)
    conta_att = Counter(g for s in att.values() for g in s)
    modello = {g for g, n in conta_cod.items() if n >= QUOTA_MODELLO * len(GREZZI_CODICE)}
    modello |= {g for g, n in conta_att.items() if n >= QUOTA_MODELLO_ATTIVITA * len(att)}
    att = {p: s - modello for p, s in att.items()}
    altre = {**{p: s - modello for p, s in GREZZI_CODICE.items()}, **att}
    indice = defaultdict(set)
    for q, s in altre.items():
        for g in s:
            indice[g].add(q)
    for p, a in att.items():
        proprie = sum(1 for g in a if conta_cod[g] == 0 and conta_att[g] == 1)
        cand = Counter(q for g in a for q in indice[g] if q != p)
        meglio = (0.0, "")
        for q, n in cand.most_common(5):
            if a and n / len(a) > meglio[0]:
                meglio = (round(n / len(a), 3), q)
        MISURA_ATT[p] = {"proprie": proprie, "sovrapposizione": meglio[0], "piu_simile": meglio[1]}
        INDICIZZA_ATT[p] = proprie >= MIN_PAROLE_PROPRIE and meglio[0] < MAX_SOVRAPPOSIZIONE_ATTIVITA


def main():
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_grafica()
    misura()
    misura_attivita()
    home()
    pagine_codice()
    da_2017()
    sic_naics()
    for a in ATTIVITA:
        pagina_attivita(a)
    indice_attivita()
    n_idx = sum(INDICIZZA.values())
    come_controlliamo(n_idx, len(INDICIZZA) - n_idx)
    about()
    privacy()
    pagina_404()
    extra()
    (DATI / "indicizzazione.json").write_text(json.dumps({
        "_nota": "Scritto da genera.py: perché ogni pagina di codice è indicizzata o no (verifica.py ricalcola le misure dalle pagine).",
        "regola": {"min_parole_proprie": MIN_PAROLE_PROPRIE, "max_sovrapposizione": MAX_SOVRAPPOSIZIONE, "quota_modello": QUOTA_MODELLO,
                   "min_proprie_con_richiesta": MIN_PROPRIE_RICHIESTA, "max_sovrapposizione_con_richiesta": MAX_SOVRAPPOSIZIONE_RICHIESTA},
        "pagine": {p: dict(MISURA[p], indicizzata=INDICIZZA[p]) for p in sorted(MISURA)},
        "regola_attivita": {"min_volume_mensile": MIN_VOLUME_ATTIVITA, "min_parole_proprie": MIN_PAROLE_PROPRIE,
                            "max_sovrapposizione": MAX_SOVRAPPOSIZIONE_ATTIVITA, "quota_modello_attivita": QUOTA_MODELLO_ATTIVITA,
                            "volumi": FILE_VOLUMI_ATTIVITA},
        "attivita": {a["slug"]: dict({"volume": volume(a), "frasi": {f: vol_frase(f) for f in a["frasi"]},
                                      "pubblicata": volume(a) >= MIN_VOLUME_ATTIVITA},
                                     **({**MISURA_ATT[a["slug"] + "/"], "indicizzata": INDICIZZA_ATT[a["slug"] + "/"]}
                                        if a["slug"] + "/" in MISURA_ATT else {})) for a in ATT}},
        ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    per_liv = Counter((C[p.rstrip("/")]["l"], INDICIZZA[p]) for p in INDICIZZA)
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili ({n_idx} pagine di codice su {len(INDICIZZA)}, "
          f"{len(INDICIZZA) - n_idx} noindex) + 404. Per livello (sì/no): "
          + ", ".join(f"{l}: {per_liv[(l, True)]}/{per_liv[(l, False)]}" for l in (2, 3, 4, 6))
          + f". Pagine attività: {len(ATTIVITA)} ({sum(INDICIZZA_ATT.values())} indicizzate"
          + (f"; noindex: {', '.join(p.rstrip('/') for p, v in INDICIZZA_ATT.items() if not v)}" if not all(INDICIZZA_ATT.values()) else "")
          + f"). Indice {len(INDICE) // 1024} KB + voci {len(FRASI) // 1024} KB.")


if __name__ == "__main__":
    main()
