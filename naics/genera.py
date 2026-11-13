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
QUOTA_MODELLO = 0.05  # gruppi di 5 parole presenti in almeno il 5% delle pagine di codice = modello della pagina, esclusi dalla misura
FRASE_FISSA = "check with the agency or form that asks for the code"

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
LIVELLO = {2: "Sector", 3: "Subsector", 4: "Industry group", 5: "NAICS industry", 6: "National industry"}


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
NA = carica("naics.json")
DOM = carica("domanda.json")
VOL = carica("volumi.json")
ATT = carica("attivita.json")["attivita"]
FAQ = carica("faq.json")["faq"]
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
_PROVA = None
MENU = [("#sectors", "Sectors"), ("naics-2017-to-2022/", "2017 → 2022"), ("sic-to-naics/", "SIC to NAICS"), ("how-we-check/", "How we check")]
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
            "controllo": data_lunga(CONTROLLO)})


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


def faq_pagina(pid, rim, extra=None):
    voci = []
    tutte = {s for v in DOM["radici"].values() for s in v}
    for x in FAQ:
        if x["pagina"] != pid:
            continue
        if x["ricerca"] not in tutte:
            raise SystemExit(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non è tra i suggerimenti salvati")
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
            + tabella(["2017 code", "2017 title (and piece moved here)"], rr))


def blocco_sic(c, rim):
    s = SIC22[c]
    righe = s["righe"]
    if not righe:
        return (f'<h2 id="sic">SIC code</h2><p>The Census concordances do not link this industry to any 1987 SIC code.'
                f'{rim.ref(["naics97_sic", "c22_17"])}</p>')
    sics = sorted({x["sic"] for x in righe})
    if s["diretto"]:
        spiega = (f"This industry has the same code and the same content since NAICS 1997, so the official Census concordance between 1987 SIC and "
                  f"1997 NAICS applies as it is.{rim.ref('naics97_sic')}")
    else:
        spiega = (f"This industry changed after 1997 (it came from {', '.join(s['n97'])} in NAICS 1997). We followed the official concordances "
                  f"2022 → 2017 → 2012 → 2007 → 2002 → 1997 and then the official 1997 NAICS ↔ 1987 SIC concordance: some SIC codes below may cover only a "
                  f"small piece of this industry.{rim.ref(['c22_17', 'c97_02', 'naics97_sic'])}")
    rr = []
    for x in righe:
        parte = '<small>Part of the SIC industry</small>' if x["parte"] else ""
        rr.append([f'<a class="cod" href="/sic-to-naics/#sic-{x["sic"]}">{x["sic"]}</a>', h(x["t"]) + parte] + ([] if s["diretto"] else [x["n97"]]))
    tab = tabella(["SIC 1987", "SIC title (and part)"] + ([] if s["diretto"] else ["Via 1997"]), rr, classe="sic-tab")
    if len(rr) > 8:
        tab = f'<details class="tutte"><summary>Show all {len(rr)} SIC lines</summary>{tab}</details>'
    return (f'<h2 id="sic">SIC code{"s" if len(sics) > 1 else ""}: {", ".join(sics[:6])}{"…" if len(sics) > 6 else ""}</h2>'
            f'<p class="small">{spiega}</p>' + tab)


def fatti(c):
    v = C[c]
    l = v["l"]
    celle = [("Code", f'<span class="cod">{c}</span>'), ("Level", LIVELLO[l] + (" (U.S.)" if l == 6 and not c.endswith("0") else ""))]
    if l == 6:
        p5 = v["p"]
        celle.append(("NAICS industry", f'<span class="cod">{p5}</span> (same)' if unico(p5) else link_cod(p5)))
        celle.append(("2017 code", ", ".join(b for b, _ in DA17[c][:3]) + ("…" if len(DA17[c]) > 3 else "")))
        sics = sorted({x["sic"] for x in SIC22[c]["righe"]})
        celle.append(("SIC 1987", (", ".join(sics[:3]) + ("…" if len(sics) > 3 else "")) if sics else "none"))
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
    corpo += blocco_2017(c, rim)
    corpo += blocco_sic(c, rim)
    p5 = v["p"]
    g4 = antenato(c, 4)
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
    testata = banda(eyebrow, f"NAICS code {c}: {v['t']}",
                    f"Official 2022 title and description, {num(len(v['idx']))} activities from the Census Bureau index, the NAICS 2017 code and the SIC equivalent.",
                    icona="tag")
    coda = f"official 2022 description, {len(v['idx'])} index activities, 2017 code and SIC equivalent."
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
]


def volume(a):
    return sum(VOL["frasi"][f]["volume"] for f in a["frasi"] if f in VOL["frasi"])


ATTIVITA = [a for a in ATT if volume(a) > 0]


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
    utili += [(f"/{a['slug']}/", a["h1"][0].upper() + a["h1"][1:], accorcia(a["descrizione"], 90)) for a in ATTIVITA]
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
                  f"several 2022 codes. Read the descriptions and {FRASE_FISSA}.", "info")
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
def pagina_attivita(a):
    rim = Rimandi()
    rx = re.compile(a["regex"], re.I)
    gruppi = defaultdict(list)
    for c in SEI:
        for e in C[c]["idx"]:
            if rx.search(e):
                gruppi[c].append(e)
    ordinati = sorted(gruppi, key=lambda c: (-len(gruppi[c]), c))
    extra = {"n_voci": num(sum(len(v) for v in gruppi.values())), "n_codici": num(len(gruppi))}
    if a.get("settore"):
        extra[f"n_sei_{a['settore']}"] = num(len(sei_di(a["settore"])))
    intro = riempi(a["intro"], extra)
    corpo = f'<div class="card pull"><p style="margin:0">{h(intro)}{rim.ref(["indice", "codici"])}</p></div>'
    corpo += '<h2 id="main-codes">The codes to look at first</h2>'
    for c in a["evidenza"]:
        v = C[c]
        prima = v["d"][0] if v["d"] else ""
        corpo += (f'<section class="voce" id="c-{c}"><h3><span class="chip-cod">{c}</span><a href="{url_di(c)}">{h(v["t"])}</a></h3>'
                  f'<div class="testo"><p>{linkifica(prima)}</p></div>')
        if gruppi.get(c):
            corpo += f'<p class="small">In the official index: {h("; ".join(gruppi[c][:6]))}{"…" if len(gruppi[c]) > 6 else ""}</p>'
        sics = sorted({x["sic"] for x in SIC22[c]["righe"]})
        if sics:
            corpo += f'<p class="small">SIC 1987: {", ".join(f"<a class=cod href=/sic-to-naics/#sic-{s}>{s}</a>" for s in sics[:6])}</p>'
        corpo += "</section>"
    corpo += rim.ref("descrizioni")
    if a.get("settore"):
        s = a["settore"]
        corpo += f'<h2 id="sector">All six-digit codes of sector {s}</h2>'
        for s3 in FIGLI[s]:
            corpo += f'<h3 class="cat-h">{link_cod(s3)} {h(C[s3]["t"])}</h3><ul class="albero">'
            corpo += "".join(f'<li>{link_cod(x)}<span>{h(C[x]["t"])}</span></li>' for x in sei_di(s3)) + "</ul>"
    rr = [[link_cod(c), h(C[c]["t"]) + f'<small>{h("; ".join(gruppi[c][:4]))}{"…" if len(gruppi[c]) > 4 else ""}</small>', num(len(gruppi[c]))] for c in ordinati]
    corpo += (f'<h2 id="index">Every {h(a["nome"])} entry of the official index, by code</h2><p class="small">Entries of the 2022 NAICS index that '
              f'match «{h(a["regex"].replace(chr(92) + "b", ""))}», grouped by six-digit code.{rim.ref("indice")}</p>'
              + tabella(["Code", "Title and entries", "Entries"], rr, num_=[2], resp="resp7"))
    corpo += nota(f"The code follows the primary activity of the establishment, not a keyword: read the description of each candidate code. "
                  f"Before using a code on a form, {FRASE_FISSA}.", "info", "alert")
    voci = faq_pagina(a["slug"], rim, extra)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    testata = banda("NAICS code by activity", a["h1"][0].upper() + a["h1"][1:], h(a["descrizione"]), icona="tag")
    pagina(a["slug"] + "/", a["titolo"], a["descrizione"], corpo, testata,
           briciole=[("Home", ""), (a["h1"][0].upper() + a["h1"][1:], a["slug"] + "/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- pagine del sito
MODULO = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card">
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or code<input type="text" name="page" required maxlength="300" placeholder="For example /541511/ or 541511"></label>
<label>What does not match the official files?<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<label>Your email (optional, only if you want a reply)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I agree that this message, and my email if I gave one, is stored to check and answer the correction (see <a href="/privacy/#corrections">privacy</a>).</span></label>
<button type="submit" class="btn">Send correction</button>
</form>"""


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
              f'own and less than {int(MAX_SOVRAPPOSIZIONE * 100)}% of text in common with the most similar page; the other {n_noidx} stay available but '
              'are not indexed and carry no ads. «NAICS code for …» pages exist only for activities with measured Google searches.</p></div>')
    corpo += ('<h2 id="updates">How often we update</h2><div class="testo"><p>Every month we download the Census files again: if a fingerprint changes we '
              'run all the checks. NAICS is revised every five years; when a new edition is published, the site moves to it.</p></div>')
    corpo += ('<h2 id="corrections">Report an error</h2><p>Found a difference with the official files? Tell us the page and, if you can, the link to the '
              'source. The email is optional.</p>' + MODULO)
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
             f'<li>We give no legal, tax or business advice: {FRASE_FISSA}.</li><li>We do not collect data about readers, apart from the optional form '
             'to report an error.</li></ul></div>'
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
             '<h2 id="corrections">Corrections form</h2><p>If you use the <a href="/how-we-check/#corrections">form to report an error</a>, we receive the page you '
             'name, your message, the source link and, only if you give it, your email address. The form is processed by Netlify Forms on our behalf. We use what '
             'you send only to check and answer the correction, and keep it only as long as that takes. The legal basis is your consent, given with the tick box; '
             'you can ask us to delete your message by sending another one through the form. There are no accounts or newsletters on this site.</p>'
             f'<h2>Your rights</h2><p>You can ask to access, correct or delete what you sent us through the same form. {cal}</p>'
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
def gruppi_di_parole(html_, n=5):
    t = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html_, flags=re.S | re.I)
    w = re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", t)).lower())
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


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
    home()
    pagine_codice()
    da_2017()
    sic_naics()
    for a in ATTIVITA:
        pagina_attivita(a)
    n_idx = sum(INDICIZZA.values())
    come_controlliamo(n_idx, len(INDICIZZA) - n_idx)
    about()
    privacy()
    pagina_404()
    extra()
    (DATI / "indicizzazione.json").write_text(json.dumps({
        "_nota": "Scritto da genera.py: perché ogni pagina di codice è indicizzata o no (verifica.py ricalcola le misure dalle pagine).",
        "regola": {"min_parole_proprie": MIN_PAROLE_PROPRIE, "max_sovrapposizione": MAX_SOVRAPPOSIZIONE, "quota_modello": QUOTA_MODELLO},
        "pagine": {p: dict(MISURA[p], indicizzata=INDICIZZA[p]) for p in sorted(MISURA)},
        "attivita": {a["slug"]: {"volume": volume(a), "pubblicata": volume(a) > 0} for a in ATT}},
        ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    per_liv = Counter((C[p.rstrip("/")]["l"], INDICIZZA[p]) for p in INDICIZZA)
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili ({n_idx} pagine di codice su {len(INDICIZZA)}, "
          f"{len(INDICIZZA) - n_idx} noindex) + 404. Per livello (sì/no): "
          + ", ".join(f"{l}: {per_liv[(l, True)]}/{per_liv[(l, False)]}" for l in (2, 3, 4, 6))
          + f". Attività pubblicate: {', '.join(a['slug'] for a in ATTIVITA)}. Indice {len(INDICE) // 1024} KB + voci {len(FRASI) // 1024} KB.")


if __name__ == "__main__":
    main()
