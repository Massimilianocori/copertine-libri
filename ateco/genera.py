"""Genera il sito statico "Codici ATECO 2025" (italiano) in ateco/sito/: una pagina per sezione, divisione e classe ATECO 2025
con titoli ufficiali, note esplicative Istat, sottocategorie, vecchi codici ATECO 2022 e coefficiente del regime forfetario.

Uso (dalla radice del repository):
    python3 -I ateco/raccolta/fonti.py        # scarica i file ufficiali -> raccolta/_grezzi/, dati/fonti.json
    python3 -I ateco/raccolta/estrai.py       # legge i file Istat -> dati/ateco.json, dati/coefficienti.json
    python3 -I ateco/raccolta/domanda.py      # ricerche vere (autocompletamento) -> dati/domanda.json
    python3 ateco/genera.py                   # pagine in ateco/sito/
    python3 ateco/verifica.py --browser       # controlli (ricalcola tutto dai file grezzi)

Livelli e pagine (decisione del 12/11/2026, lezione AdSense «scarso valore»): le 1.290 sottocategorie non hanno una pagina
ciascuna, perché 725 hanno lo stesso titolo della classe o della categoria sopra di loro e quasi tutte hanno 1-3 note. La pagina è
la CLASSE (4 cifre, 651 pagine): dentro, ogni categoria e sottocategoria è una sezione con ancora (#c-56.11.11), le sue note, i
vecchi codici e il coefficiente. Sezioni (22) e divisioni (87) sono pagine indice con le loro note; i gruppi sono capitoli della
divisione (#g-56.1). Una pagina si indicizza solo se ha abbastanza testo proprio (vedi MIN_PAROLE_PROPRIE e MAX_SOVRAPPOSIZIONE);
le altre restano consultabili, noindex, fuori dalla sitemap e senza pubblicità.
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

URL_SITO = "https://codici-ateco.netlify.app"  # unico punto da cambiare (anche in verifica.py) se il nome del sito su Netlify è diverso
NOME = "Codici ATECO 2025"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti della rete)
GOOGLE_VERIFICA_2 = "fCopHfbOO5n6WfdF7-ZnrX4BCGXMGDkT_Qfsb4lKR4o"  # Search Console, tag della proprietà nuova (12/11/2026 sera): non rimuoverlo
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "ateco"  # nome del sito in monetizzazione.json
MIN_PAROLE_ADSENSE = 400  # niente pubblicità nelle pagine noindex o con poco testo (lezione AdSense «scarso valore»)
MIN_PAROLE_PROPRIE = 150  # parole (gruppi di 5) che non compaiono in nessun'altra pagina di codice: sotto, la pagina è noindex
MAX_SOVRAPPOSIZIONE = 0.55  # quota del testo in comune con la pagina di codice più simile: da qui in su, noindex
FRASE_FISSA = "verifica con il commercialista o la Camera di commercio"
FILE_VOLUMI_ATTIVITA = "volumi-attivita-2026-11-13.json"  # misura con data: per rifarla, file nuovo con la data e nome qui (e in verifica.py)
MIN_VOLUME_ATTIVITA = 100  # pagina «Codice ATECO per …» solo con almeno 100 ricerche al mese misurate su una delle sue frasi
MAX_SOVRAPPOSIZIONE_ATTIVITA = 0.40  # pagine attività: più severa delle pagine di codice (stessa scelta di naics/ dopo la revisione del 13/11)
QUOTA_MODELLO_ATTIVITA = 0.25  # frasi presenti in almeno un quarto delle pagine attività = modello, non contano come testo proprio
MAX_RIGHE_CODICE = 5  # righe delle note Istat mostrate per codice nella tabella delle scelte (se non scelte a mano)
MAX_ESCLUSIONI = 10  # note «Non comprende» mostrate per pagina attività

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
LIVELLI = {1: "sezione", 2: "divisione", 3: "gruppo", 4: "classe", 5: "categoria", 6: "sottocategoria"}


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
AT = carica("ateco.json")
CO = carica("coefficienti.json")
DOM = carica("domanda.json")
VOL = carica("volumi.json")
MES = carica("mestieri.json")["mestieri"]
FAQ = carica("faq.json")["faq"]
ATT = carica("attivita.json")["attivita"]
VOLA = carica(FILE_VOLUMI_ATTIVITA)
AFF = carica("affiliati.json")
C = AT["codici"]
OP = AT["operativa"]
RAC = AT["raccordo"]
GRUPPO22 = CO["gruppo_per_codice_2022"]
TABCO = CO["tabella"]
CONTROLLO = max(date.fromisoformat(x["letto_il"]) for x in list(FJ["file"].values()) + list(FJ["pagine"].values()))


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    g = "1°" if d.day == 1 else str(d.day)
    return f"{g} {MESI[d.month - 1]} {d.year}"


def num(n):
    return f"{n:,}".replace(",", ".")


def maiuscola(t):
    return t[0].upper() + t[1:]


def accorcia(s, n):
    if len(s) <= n:
        return s
    t = s[:n - 1].rsplit(" ", 1)[0].rstrip(",;:(-– ")
    return t + "…"


# ---------------------------------------------------------------- albero
FIGLI = defaultdict(list)
for c, v in sorted(C.items(), key=lambda kv: kv[1]["o"]):
    if v["p"]:
        FIGLI[v["p"]].append(c)
ORDINE = sorted(C, key=lambda c: C[c]["o"])
SEZIONI = [c for c in ORDINE if C[c]["l"] == 1]
DIVISIONI = [c for c in ORDINE if C[c]["l"] == 2]
CLASSI = [c for c in ORDINE if C[c]["l"] == 4]


def antenato(c, liv):
    while C[c]["l"] > liv:
        c = C[c]["p"]
    return c


def sottocategorie(c):
    if C[c]["l"] == 6:
        return [c]
    return [x for f in FIGLI[c] for x in sottocategorie(f)]


def codice_principale(classe):
    """Il codice da mostrare per la classe: la sottocategoria se è l'unica, altrimenti la classe."""
    s = sottocategorie(classe)
    return s[0] if len(s) == 1 else classe


def url_di(c):
    """Indirizzo della pagina (con ancora) che contiene il codice ATECO 2025 c."""
    l = C[c]["l"]
    if l == 1:
        return f"/sezione-{c.lower()}/"
    if l == 2:
        return f"/{c}/"
    if l == 3:
        return f"/{c[:2]}/#g-{c}"
    if l == 4:
        return f"/{c.replace('.', '-')}/"
    return f"/{antenato(c, 4).replace('.', '-')}/#c-{c}"


def percorso_pagina(c):
    return url_di(c).split("#")[0].lstrip("/")


# ---------------------------------------------------------------- raccordo e coefficienti
RAC25 = defaultdict(list)  # codice 2025 -> righe del raccordo
RAC22 = defaultdict(list)
for r in RAC:
    RAC25[r["c25"]].append(r)
    if r["c22"]:
        RAC22[r["c22"]].append(r)
OP_PER25 = defaultdict(list)  # codice 2025 rappresentativo -> codici 2022 (tabella operativa, solo 6 cifre)
for c22, v in OP.items():
    if v["l"] == 6:
        for x in {v["rap"], v["cam"]} - {None}:
            OP_PER25[x].append(c22)


RIMANDI_IN = defaultdict(list)  # classe -> [(codice da cui viene l'esclusione, testo)]
for _c, _v in C.items():
    for _n in _v["note"]:
        if _n["t"] == 3:
            for _r in _n["rif"]:
                if _r in C and C[_r]["l"] >= 4:
                    _cl = _r if C[_r]["l"] == 4 else None
                    if _cl is None:
                        _x = _r
                        while C[_x]["l"] > 4:
                            _x = C[_x]["p"]
                        _cl = _x
                    if _c[:5] != _cl[:5] and (_c, _n["it"]) not in RIMANDI_IN[_cl]:
                        RIMANDI_IN[_cl].append((_c, _n["it"]))


def vecchi_di(sc):
    """Righe del raccordo al sesto livello per la sottocategoria 2025 sc."""
    return [r for r in RAC25[sc] if r["c22"] and len(r["c22"]) == 8]


def gruppi_coeff(sc):
    return sorted({GRUPPO22[r["c22"]] for r in vecchi_di(sc)}, key=int) if vecchi_di(sc) else []


def coeff_txt(g):
    t = TABCO[str(g)]
    return f'{t["coefficiente"]}%'


# ---------------------------------------------------------------- fonti e rimandi
FONTI_DEF = {}
for fid, f in FJ["file"].items():
    FONTI_DEF[fid] = {"titolo": f["titolo"], "chi": f["chi"], "url": FJ["pagine"][f["pagina"]]["url"] if f.get("pagina") else f["url"],
                      "file": f["url"], "letto": f["letto_il"]}
for pid, p in FJ["pagine"].items():
    FONTI_DEF[pid] = {"titolo": p["titolo"], "chi": p["chi"], "url": p["url"], "file": None, "letto": p["letto_il"]}


class Rimandi:
    def __init__(self):
        self.ordine = []

    def ref(self, ids):
        if isinstance(ids, str):
            ids = [ids]
        nums = []
        for i in ids:
            if i not in FONTI_DEF:
                raise SystemExit(f"fonte sconosciuta: {i}")
            if i not in self.ordine:
                self.ordine.append(i)
            nums.append(self.ordine.index(i) + 1)
        return '<sup class="ref">' + ",".join(f'<a href="#f{n}" aria-label="fonte {n}">[{n}]</a>' for n in sorted(set(nums))) + "</sup>"

    def elenco(self):
        if not self.ordine:
            return ""
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = FONTI_DEF[i]
            file_ = f' <a href="{h(f["file"])}" rel="noopener">File</a>.' if f["file"] else ""
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}.{file_}</li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Fonti</h2><ol>{"".join(voci)}</ol>'
                f'<p class="small">Letti il {data_lunga(CONTROLLO)}. Testi Istat in licenza CC BY 4.0, senza modifiche. <a href="/come-lavoriamo/">Come lavoriamo</a>.</p></section>')


ATTRIBUZIONE = (f'Fonte dei codici, dei titoli e delle note: Istat, classificazione ATECO 2025 (struttura, note esplicative, tavola di raccordo e '
                f'tabella operativa, aggiornamento 2026), licenza <a href="{FJ["licenza"]["url"]}" rel="noopener">CC BY 4.0</a>. I testi Istat sono '
                'riportati senza modifiche; impaginazione, collegamenti, conteggi e abbinamento ai coefficienti del forfettario sono nostri.')


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
INDICIZZA = {}  # percorso -> True/False (pagine di codice)
_PROVA = None  # dizionario: pagina() raccoglie il testo invece di scrivere (misura della sovrapposizione)
MENU = [("#sezioni", "Codici"), ("da-ateco-2022-a-2025/", "Da 2022 a 2025"), ("cosa-cambia-ateco-2025/", "Cosa cambia"),
        ("coefficienti-redditivita-forfettario/", "Forfettario"), ("codice-ateco-per/", "Per attività")]
DISCLAIMER = ("<strong>Informazioni dalle tabelle ufficiali Istat e dai testi di legge, non una consulenza.</strong> Il codice ATECO giusto dipende "
              f"dall'attività svolta davvero e la scelta del regime fiscale dalla tua situazione: {FRASE_FISSA}. Sito indipendente, non affiliato a "
              "Istat, all'Agenzia delle entrate o alle Camere di commercio.")


def parole_principali(corpo):
    t = re.sub(r"<section data-ripreso>.*?</section>", " ", corpo, flags=re.S)  # link alle guide: non contano come testo della pagina
    t = re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", t, flags=re.S | re.I)
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
        bc = ('<nav class="briciole" aria-label="Percorso">' + " › ".join([f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    con_pub = indicizza and parole_principali(testata + corpo) >= MIN_PAROLE_ADSENSE
    adsense = MON.script_adsense(SITO_ID, con_pub)
    corpo_tr = corpo + MON.riga_trasparenza(corpo, "it")
    testo = f"""<!DOCTYPE html>
<html lang="it">
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
<meta property="og:locale" content="it_IT">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14213D">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Vai al contenuto</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Codici <b>ATECO</b> 2025</span></a>
<nav class="menu" aria-label="Principale">{menu_html(percorso)}</nav>
<button type="button" class="tema" data-tema aria-label="Tema chiaro o scuro">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Menu">{ico("menu")}</summary><nav aria-label="Principale">{menu_html(percorso)}</nav></details>
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
<a class="logo" href="/">{LOGO}<span>Codici <b>ATECO</b> 2025</span></a>
<p><strong>{NOME}</strong> mette in pagine leggibili la classificazione ATECO 2025 dell'Istat: titoli ufficiali, note su cosa è incluso ed
escluso, vecchi codici ATECO 2022 e coefficienti del forfettario dalla legge. Sito indipendente, non affiliato a Istat, all'Agenzia delle entrate o alle
Camere di commercio.</p>
<p>{ATTRIBUZIONE}</p>
</div><div>
<h2>Codici</h2><ul><li><a href="/#cerca">Cerca un codice</a></li><li><a href="/#sezioni">Tutte le sezioni</a></li>
<li><a href="/da-ateco-2022-a-2025/">Da ATECO 2022 a 2025</a></li><li><a href="/cosa-cambia-ateco-2025/">Cosa cambia dal 2025</a></li>
<li><a href="/coefficienti-redditivita-forfettario/">Coefficienti del forfettario</a></li>
<li><a href="/codice-ateco-per/">Codice ATECO per attività</a></li></ul>
</div><div>
<h2>Il sito</h2><ul><li><a href="/come-lavoriamo/">Come lavoriamo</a></li><li><a href="/come-lavoriamo/#segnala">Segnala un errore</a></li>
<li><a href="/chi-siamo/">Chi siamo</a></li><li><a href="/privacy/">Privacy</a></li></ul>
</div></div>
<p class="f-base">Informazioni generali dalle tabelle ufficiali, non consulenza fiscale: {FRASE_FISSA}. La classificazione originale è sul sito
dell'<a href="https://www.istat.it/classificazione/ateco-2025/" rel="noopener">Istat</a>.</p>
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


def tabella(intest, righe, caption="", num_=None, attr=None, id_=None, resp="", etichette=None):
    num_ = num_ or []
    th = "".join(f'<th scope="col"{" class=\"n\"" if i in num_ else ""}>{x}</th>' for i, x in enumerate(intest))
    etich = etichette or [re.sub(r"<[^>]+>", "", x) for x in intest]
    body = ""
    for k, r in enumerate(righe):
        at = attr[k] if attr else ""
        body += f"<tr{at}>" + "".join(f'<td{" class=\"n\"" if i in num_ else ""}{f" data-l=\"{h(etich[i])}\"" if resp and i else ""}>{x}</td>'
                                      for i, x in enumerate(r)) + "</tr>"
    cap = f"<caption>{caption}</caption>" if caption else ""
    idt = f' id="{id_}"' if id_ else ""
    return f'<div class="tab"><table class="dati{" " + resp if resp else ""}"{idt}>{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def nota(testo, tipo="info", icona="info"):
    return f'<div class="nota {tipo}">{ico(icona)}<p>{testo}</p></div>'


def faq_html(voci, titolo="Domande frequenti"):
    """voci: [(domanda, risposta_testo, rimando_html)] -> (html, json-ld)."""
    if not voci:
        return "", None
    blocchi = "".join(f'<div class="faq"><h3>{h(q)}</h3><p>{h(a)}{ref}</p></div>' for q, a, ref in voci)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a, _ in voci]}
    return (f'<h2 id="faq">{h(titolo)}</h2><p class="small">Domande che le persone cercano davvero su Google, con la risposta presa dalle fonti '
            'ufficiali citate.</p>' + blocchi), ld


def link_cod(c, testo=None):
    return f'<a class="cod" href="{url_di(c)}">{h(testo or c)}</a>'


# ---------------------------------------------------------------- note Istat
TIPI_NOTA = {1: None, 2: "Comprende", 5: "Comprende anche", 3: "Non comprende", 6: "Nota operativa Istat"}


def linkifica(testo, rif):
    """Collega i codici citati dopo «cfr.» alle loro pagine (il testo resta quello di Istat)."""
    t = h(testo)
    if not rif:
        return t
    i = t.rfind("cfr.")
    if i < 0:
        return t
    testa, coda = t[:i], t[i:]
    for c in sorted(rif, key=len, reverse=True):
        if c in C:
            coda = re.sub(r"(?<![\w.])" + re.escape(c) + r"(?![\w.]*\d)", lambda m: f'<a class="cod" href="{url_di(c)}">{c}</a>', coda, count=1)
    return testa + coda


def lista_note(note, classe=""):
    """Note di uno stesso tipo come elenco; le voci S seguono la voce P precedente come sotto-elenco."""
    out, aperta = [], False
    for n in note:
        if n["s"] == "S" and out:
            if not aperta:
                out[-1] = out[-1][:-5] + "<ul>"
                aperta = True
            out[-1] += f"<li>{linkifica(n['it'], n['rif'])}</li>"
        else:
            if aperta:
                out[-1] += "</ul></li>"
                aperta = False
            out.append(f"<li>{linkifica(n['it'], n['rif'])}</li>")
    if aperta:
        out[-1] += "</ul></li>"
    return f'<ul{f" class={chr(34)}{classe}{chr(34)}" if classe else ""}>{"".join(out)}</ul>'


def note_html(c, rim):
    note = C[c]["note"]
    if not note:
        return ""
    ref = rim.ref("note")
    out = ""
    centrali = [n for n in note if n["t"] == 1]
    if centrali:
        blocchi, lista = [], []
        for n in centrali:
            if n["s"] == "S":
                lista.append(f"<li>{linkifica(n['it'], n['rif'])}</li>")
            else:
                if lista:
                    blocchi.append(f"<ul>{''.join(lista)}</ul>")
                    lista = []
                blocchi.append(f"<p>{linkifica(n['it'], n['rif'])}</p>")
        if lista:
            blocchi.append(f"<ul>{''.join(lista)}</ul>")
        out += "".join(blocchi)
    for t in (2, 5, 3):
        sel = [n for n in note if n["t"] == t]
        if sel:
            out += f"<h4>{TIPI_NOTA[t]}</h4>" + lista_note(sel, "escl" if t == 3 else "")
    op = [n for n in note if n["t"] == 6]
    if op:
        out += f'<h4>{TIPI_NOTA[6]}</h4><div class="op">' + "".join(f"<p>{linkifica(n['it'], n['rif'])}</p>" for n in op) + "</div>"
    return f'<div class="note">{out}<p class="mini">Note esplicative Istat ATECO 2025{ref}</p></div>'


def lingue(c):
    v = C[c]
    return f'<p class="en" lang="en"><b>EN</b> {h(v["en"])} · <span lang="de"><b>DE</b> {h(v["de"])}</span></p>'


COPERTURA = {"TOTALE": "tutto", "PARZIALE": "in parte"}


UNO_A_UNO = "il contenuto della sottocategoria di ATECO 2025 è interamente coperto dalla corrispondente sottocategoria di ATECO 2022 e viceversa"


def comune_html(t):
    if t.startswith(UNO_A_UNO):
        return "identico (uno a uno)"
    return f'<span class="comune">{h(t)}</span>'


def blocco_vecchi(sc, rim):
    righe = vecchi_di(sc)
    if not righe:
        return nota("La tavola di raccordo Istat non collega questo codice a nessun codice ATECO 2022: è un codice nuovo, senza un "
                    f"corrispondente nella classificazione precedente.{rim.ref('raccordo')}", "info")
    if len(righe) == 1 and righe[0]["comune"].startswith(UNO_A_UNO):
        r = righe[0]
        return (f'<p class="coef"><span>Vecchio codice ATECO 2022:</span> <a class="cod" href="/da-ateco-2022-a-2025/#v-{r["c22"]}">{r["c22"]}</a> '
                f'«{h(OP[r["c22"]]["t22"])}», stesso contenuto{rim.ref("raccordo")}</p>')
    rr = []
    for r in righe:
        rr.append([f'<a class="cod" href="/da-ateco-2022-a-2025/#v-{r["c22"]}">{r["c22"]}</a>', h(OP[r["c22"]]["t22"]),
                   f'{COPERTURA.get(r["cop22"], r["cop22"])}', comune_html(r["comune"])])
    return (f'<h4>Vecchi codici ATECO 2022 ({len(righe)}){rim.ref("raccordo")}</h4>'
            + tabella(["ATECO 2022", "Titolo 2022", "Confluisce qui", "Contenuto in comune (Istat)"], rr, resp="resp7"))


def blocco_coeff(sc, rim):
    """Riga del forfettario di una sottocategoria: la percentuale è una nostra derivazione dai vecchi codici della tavola di raccordo
    (la legge chiede il codice ATECO 2007 dell'attività) e la riga lo dice sempre, con i vecchi codici usati."""
    g = gruppi_coeff(sc)
    if not g:
        return (f'<p class="coef"><span>Forfettario:</span> nessun codice ATECO 2022 corrispondente nella tavola Istat, quindi il coefficiente non si '
                f'ricava da qui{rim.ref("dlgs81_art1")}.</p>')
    tutti = sorted({r["c22"] for r in vecchi_di(sc)})
    percentuali = sorted({TABCO[str(x)]["coefficiente"] for x in g})
    da = f'dal vecchio codice {tutti[0]}' if len(tutti) == 1 else f'dai vecchi codici {", ".join(tutti)}'
    coda = (f' <span class="mini">Derivazione nostra {da}: per la legge conta il codice ATECO 2007 della tua attività, verifica con il '
            f'commercialista.</span>{rim.ref(["l190_all4", "dlgs81_art1", "raccordo"])}</p>')
    if len(percentuali) == 1:
        nomi = " e ".join(f'«<a href="/coefficienti-redditivita-forfettario/">{h(TABCO[str(x)]["gruppo"])}</a>»' for x in g)
        return (f'<p class="coef"><span>Forfettario, ricavato dai vecchi codici:</span> <b>{percentuali[0]}%</b> <span class="mini">'
                f'{"gruppo" if len(g) == 1 else "gruppi"} {nomi} della tabella di legge{", stessa percentuale" if len(g) > 1 else ""}.</span>' + coda)
    parti = []
    for perc in percentuali:  # una voce per percentuale: due gruppi di legge con la stessa percentuale non si ripetono
        cods = sorted({r["c22"] for r in vecchi_di(sc) if TABCO[str(GRUPPO22[r["c22"]])]["coefficiente"] == perc})
        parti.append(f'<b>{perc}%</b> se il vecchio codice era {", ".join(cods)}')
    return (f'<p class="coef"><span>Forfettario, secondo il vecchio codice dell\'attività:</span> {"; ".join(parti)}.'
            f' <span class="mini">Derivazione nostra dalla tavola di raccordo: per la legge conta il codice ATECO 2007 della tua attività, verifica con '
            f'il commercialista quale percentuale si applica.</span>{rim.ref(["l190_all4", "dlgs81_art1", "raccordo"])}</p>')


def voce_sottocategoria(sc, rim, hn="h3"):
    return (f'<section class="voce" id="c-{sc}"><{hn}><span class="chip-cod">{sc}</span> {h(C[sc]["it"])}</{hn}>{lingue(sc)}'
            f'{note_html(sc, rim)}{blocco_vecchi(sc, rim)}{blocco_coeff(sc, rim)}</section>')


# ---------------------------------------------------------------- pagine di codice
def titolo_codice(cod, testo, prefisso="Codice ATECO "):
    base = f"{prefisso}{cod}: "
    return base + accorcia(testo, 65 - len(base))


def descr_codice(cod, testo, coda):
    base = f"Codice ATECO 2025 {cod} «"
    spazio = 160 - len(base) - len("»: ") - len(coda)
    return f"{base}{accorcia(testo, spazio)}»: {coda}"


def pagina_classe(cl):
    rim = Rimandi()
    princ = codice_principale(cl)
    subs = sottocategorie(cl)
    div, gru, sez = antenato(cl, 2), antenato(cl, 3), antenato(cl, 1)
    v = C[cl]
    vecchi = sorted({r["c22"] for s in subs for r in vecchi_di(s)})
    gruppi = sorted({g for s in subs for g in gruppi_coeff(s)}, key=int)
    perc_cl = sorted({TABCO[str(g)]["coefficiente"] for g in gruppi})
    coeff = (f"{perc_cl[0]}%" if len(perc_cl) == 1 else ("dipende" if gruppi else "—"))
    cifre = (f'<div class="card pull cifre"><div class="cifra main"><b class="cod">{princ}</b><span>{"sottocategoria" if princ != cl else "classe"} '
             f'ATECO 2025</span></div><div class="cifra"><b>{len(subs)}</b><span>{"sottocategoria" if len(subs) == 1 else "sottocategorie"} da 6 cifre</span></div>'
             f'<div class="cifra"><b>{len(vecchi)}</b><span>{"codice ATECO 2022 collegato" if len(vecchi) == 1 else "codici ATECO 2022 collegati"}</span></div>'
             f'<div class="cifra"><b>{coeff}</b><span>forfettario, dai vecchi codici</span></div>'
             '</div>')
    corpo = cifre
    if len(subs) > 1:
        corpo += ('<ul class="livelli" aria-label="Sottocategorie">' + "".join(f'<li><a href="#c-{s}">{s}</a></li>' for s in subs) + "</ul>")
        if v["note"]:
            corpo += f'<h2 id="classe">Cosa comprende la classe {cl}</h2>' + note_html(cl, rim)
        for cat in FIGLI[cl]:
            figli = FIGLI[cat]
            if len(figli) > 1 or C[cat]["it"] != C[figli[0]]["it"]:
                corpo += f'<h2 class="cat-h" id="c-{cat}"><span class="chip-cod">{cat}</span> {h(C[cat]["it"])}</h2><p class="small">Categoria ATECO 2025</p>{lingue(cat)}'
            else:
                corpo += f'<span id="c-{cat}"></span>'  # categoria con lo stesso titolo della sua unica sottocategoria
            if C[cat]["note"]:
                corpo += note_html(cat, rim)
            for s in figli:
                corpo += voce_sottocategoria(s, rim, "h3")
    else:
        # una sola sottocategoria: note della classe e della sottocategoria nella stessa scheda
        corpo += '<h2 id="cosa-comprende">Cosa comprende</h2>'
        for x in [cl] + [c for c in FIGLI[cl]]:
            if x != cl:
                corpo += f'<span id="c-{x}"></span>'
            if C[x]["note"]:
                corpo += note_html(x, rim)
        if not any(C[x]["note"] for x in [cl] + FIGLI[cl] + subs):
            corpo += '<p class="small">Per questo codice Istat non pubblica note esplicative: vale il titolo.</p>'
        sc = princ
        corpo += (f'<section class="voce" id="c-{sc}"><h2><span class="chip-cod">{sc}</span> {h(C[sc]["it"])}</h2>{lingue(sc)}'
                  f'{note_html(sc, rim)}{blocco_vecchi(sc, rim)}{blocco_coeff(sc, rim)}</section>')
    # codici 2022 che la tabella operativa riporta qui
    op_qui = sorted({c22 for s in subs + [cl] + FIGLI[cl] for c22 in OP_PER25.get(s, [])})
    if op_qui and set(op_qui) != set(vecchi):
        rr = []
        for c22 in op_qui:
            o = OP[c22]
            dest = o["rap"] if o["rap"] else "—"
            cam = o["cam"] if o["cam"] and o["cam"] != o["rap"] else ""
            rr.append([f'<a class="cod" href="/da-ateco-2022-a-2025/#v-{c22}">{c22}</a>', h(o["t22"]), link_cod(dest) + (f' <span class="mini">(Camere di commercio: {link_cod(cam)})</span>' if cam else "")])
        corpo += (f'<h2 id="tabella-operativa">Vecchi codici riclassificati qui</h2><p class="small">Tabella operativa Istat di riclassificazione.{rim.ref("operativa")}</p>'
                  + tabella(["ATECO 2022", "Titolo 2022", "Nuovo codice rappresentativo"], rr, resp="resp7"))
    # esclusioni di altri codici che rimandano qui
    rim_qui = RIMANDI_IN.get(cl, [])
    if rim_qui:
        corpo += (f'<h2 id="rimandi">Attività che Istat rimanda a questa classe</h2><p class="small">Note di esclusione di altri codici che indicano '
                  f'{"questa classe" if princ == cl else "questo codice"}.{rim.ref("note")}</p><ul class="albero">')
        for da, testo in rim_qui[:40]:
            corpo += f'<li>{link_cod(da)}<span>{h(testo)}</span></li>'
        corpo += "</ul>"
    corpo += blocco_guide(cl)
    # dove sta
    fratelli = [x for x in FIGLI[gru] if C[x]["l"] == 4]
    corpo += f'<h2 id="albero">Dove si trova nella classificazione</h2><ul class="albero">'
    corpo += f'<li><span class="cod">{sez}</span><span>Sezione: <a href="{url_di(sez)}">{h(C[sez]["it"].capitalize())}</a></span></li>'
    corpo += f'<li><span class="cod">{div}</span><span>Divisione: <a href="{url_di(div)}">{h(C[div]["it"])}</a></span></li>'
    corpo += f'<li><span class="cod">{gru}</span><span>Gruppo: <a href="{url_di(gru)}">{h(C[gru]["it"])}</a></span></li>'
    corpo += "</ul>"
    if len(fratelli) > 1:
        corpo += (f'<h3>Altre classi del gruppo {gru}</h3><ul class="albero">' + "".join(
            f'<li><a class="cod" href="{url_di(x)}">{codice_principale(x)}</a><span>{h(C[x]["it"])}</span></li>' for x in fratelli if x != cl) + "</ul>")
    corpo += box_affiliati(False)
    corpo += rim.elenco()
    eyebrow = f"Classe ATECO 2025 · sezione {sez}"
    titolo_h1 = f"Codice ATECO {princ}: {v['it']}"
    sub = f'Divisione {div} «{h(accorcia(C[div]["it"], 90))}»'

    extra = f'<p class="altre-lingue"><b>EN</b> {h(v["en"])} · <b>DE</b> {h(v["de"])}</p>'
    testata = banda(eyebrow, titolo_h1, sub, extra)
    coda = (f"note Istat, vecchio codice {vecchi[0]} e forfettario." if len(vecchi) == 1 else
            f"note Istat, {len(subs)} sottocategorie, vecchi codici 2022 e forfettario." if len(subs) > 1 else "note Istat, vecchi codici 2022 e forfettario.")
    perc = percorso_pagina(cl)
    pagina(perc, titolo_codice(princ, v["it"]), descr_codice(princ, v["it"], coda), corpo, testata,
           briciole=[("Home", ""), (f"Sezione {sez}", percorso_pagina(sez)), (f"Divisione {div}", percorso_pagina(div)), (f"Classe {cl}", perc)],
           indicizza=INDICIZZA.get(perc, True))


def pagina_divisione(dv):
    rim = Rimandi()
    sez = antenato(dv, 1)
    v = C[dv]
    gruppi = FIGLI[dv]
    classi = [c for g in gruppi for c in FIGLI[g]]
    subs = [s for c in classi for s in sottocategorie(c)]
    corpo = (f'<div class="card pull cifre"><div class="cifra main"><b class="cod">{dv}</b><span>divisione ATECO 2025</span></div>'
             f'<div class="cifra"><b>{len(gruppi)}</b><span>{"gruppo" if len(gruppi) == 1 else "gruppi"}</span></div>'
             f'<div class="cifra"><b>{len(classi)}</b><span>{"classe" if len(classi) == 1 else "classi"}</span></div>'
             f'<div class="cifra"><b>{len(subs)}</b><span>sottocategorie da 6 cifre</span></div></div>')
    if v["note"]:
        corpo += f'<h2 id="cosa-comprende">Cosa comprende la divisione {dv}</h2>' + note_html(dv, rim)
    for g in gruppi:
        corpo += f'<h2 id="g-{g}"><span class="chip-cod">{g}</span> {h(C[g]["it"])}</h2>'
        if C[g]["note"]:
            corpo += note_html(g, rim)
        corpo += '<ul class="albero">'
        for c in FIGLI[g]:
            ss = sottocategorie(c)
            pr = codice_principale(c)
            dett = f'<span class="mini">{len(ss)} sottocategorie: {", ".join(ss[:8])}{"…" if len(ss) > 8 else ""}</span>' if len(ss) > 1 else ""
            corpo += f'<li><a class="cod" href="{url_di(c)}">{pr}</a><span>{h(C[c]["it"])}</span>{dett}</li>'
        corpo += "</ul>"
    # coefficienti possibili
    cnt = Counter(g for s in subs for g in gruppi_coeff(s))
    if cnt:
        rr = [[f"{TABCO[str(g)]['coefficiente']}%", h(TABCO[str(g)]["gruppo"]), num(n)] for g, n in sorted(cnt.items(), key=lambda kv: -kv[1])]
        corpo += (f'<h2 id="forfettario">Coefficienti del forfettario nella divisione {dv}</h2><p class="small">Per ogni sottocategoria il coefficiente '
                  f'dipende dal codice ATECO 2007 di provenienza: qui quante sottocategorie della divisione hanno vecchi codici in ciascun gruppo dell\'allegato 4 '
                  f'della legge 190/2014.{rim.ref(["raccordo", "l190_all4", "dlgs81_art1"])}</p>'
                  + tabella(["Coefficiente", "Gruppo", "Sottocategorie"], rr, num_=[2]))
    corpo += (f'<h2 id="albero">Dove si trova</h2><ul class="albero"><li><span class="cod">{sez}</span><span>Sezione: '
              f'<a href="{url_di(sez)}">{h(C[sez]["it"].capitalize())}</a></span></li></ul>')
    corpo += rim.elenco()
    testata = banda(f"Divisione ATECO 2025 · sezione {sez}", f"Codici ATECO {dv}: {v['it']}",
                    f"Tutti i gruppi e le classi della divisione {dv}, con le note Istat su cosa comprende.",
                    f'<p class="altre-lingue"><b>EN</b> {h(v["en"])} · <b>DE</b> {h(v["de"])}</p>')
    perc = percorso_pagina(dv)
    pagina(perc, titolo_codice(dv, v["it"], "Codici ATECO "), descr_codice(dv, v["it"], f"{len(classi)} classi e {len(subs)} sottocategorie con note Istat."),
           corpo, testata, briciole=[("Home", ""), (f"Sezione {sez}", percorso_pagina(sez)), (f"Divisione {dv}", perc)], indicizza=INDICIZZA.get(perc, True))


def pagina_sezione(sz):
    rim = Rimandi()
    v = C[sz]
    divs = FIGLI[sz]
    nome = v["it"][0] + v["it"][1:].lower()
    corpo = (f'<div class="card pull cifre"><div class="cifra main"><b class="cod">{sz}</b><span>sezione ATECO 2025</span></div>'
             f'<div class="cifra"><b>{len(divs)}</b><span>{"divisione" if len(divs) == 1 else "divisioni"}</span></div>'
             f'<div class="cifra"><b>{sum(len([c for g in FIGLI[d] for c in FIGLI[g]]) for d in divs)}</b><span>classi</span></div>'
             f'<div class="cifra"><b>{sum(len(sottocategorie(d)) for d in divs)}</b><span>sottocategorie da 6 cifre</span></div></div>')
    if v["note"]:
        corpo += f'<h2 id="cosa-comprende">Cosa comprende la sezione {sz}</h2>' + note_html(sz, rim)
    corpo += f'<h2 id="divisioni">Divisioni della sezione {sz}</h2><ul class="albero">'
    for d in divs:
        corpo += f'<li><a class="cod" href="{url_di(d)}">{d}</a><span>{h(C[d]["it"])}</span><span class="mini">{len(sottocategorie(d))} sottocategorie</span></li>'
    corpo += "</ul>" + rim.elenco()
    testata = banda("Sezione ATECO 2025", f"Sezione {sz}: {nome}", f"Le divisioni della sezione {sz} con le note Istat su cosa comprende.",
                    f'<p class="altre-lingue"><b>EN</b> {h(v["en"])} · <b>DE</b> {h(v["de"])}</p>')
    perc = percorso_pagina(sz)
    pagina(perc, f"Codici ATECO sezione {sz}: " + accorcia(nome, 65 - len(f"Codici ATECO sezione {sz}: ")),
           f"Sezione {sz} di ATECO 2025 «{accorcia(nome, 160 - 60 - len(sz))}»: divisioni, classi e note Istat.",
           corpo, testata, briciole=[("Home", ""), (f"Sezione {sz}", perc)], indicizza=INDICIZZA.get(perc, True))


# ---------------------------------------------------------------- numeri generali
OP6 = {k: v for k, v in OP.items() if v["l"] == 6}
NUM = {f"n_{l}": num(sum(1 for v in C.values() if v["l"] == l)) for l in range(1, 7)}
NUM.update({"n_tot": num(len(C)), "sez_96": antenato("96", 1), "n22_6": num(len(OP6)),
            "n22_11": num(sum(1 for v in OP6.values() if v["tipo"] == "1-1")), "n22_n1": num(sum(1 for v in OP6.values() if v["tipo"] == "N-1")),
            "n22_c": num(sum(1 for v in OP6.values() if v["ric"] == "C")),
            "n_ecom": num(len([r for r in RAC22["47.91.10"] if len(r["c25"]) == 8])),
            "tabella_coeff": "; ".join(f'{t["coefficiente"]}% per «{t["gruppo"]}»' for _, t in sorted(TABCO.items(), key=lambda kv: int(kv[0])))})


def controlla_titoli_citati(testo, dove):
    """Ogni «codice «titolo»» citato in un testo scritto da noi deve avere il titolo ufficiale (2025 o 2022)."""
    for cod, tit in re.findall(r"(\d{2}\.\d{2}\.\d{2}) «([^»]+)»", testo):
        ok = (cod in C and C[cod]["it"] == tit) or (cod in OP and OP[cod]["t22"] == tit)
        if not ok:
            raise SystemExit(f"{dove}: il titolo citato per {cod} («{tit}») non è quello ufficiale")


def faq_pagina(pid, rim):
    voci = []
    tutte = {s for v in DOM["radici"].values() for s in v}
    for x in FAQ:
        if x["pagina"] != pid:
            continue
        if x["ricerca"] not in tutte:
            raise SystemExit(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non è tra i suggerimenti salvati")
        a = x["a"].format(**NUM)
        controlla_titoli_citati(a, f"FAQ {pid}")
        voci.append((x["q"], a, rim.ref(x["fonti"])))
    return voci


def box_affiliati(mostra=True):
    voci = [v for k, v in AFF.items() if not k.startswith("_") and v.get("url")]
    if not mostra or not voci:
        return ""
    righe = "".join(f'<li><a href="{h(v["url"])}" rel="sponsored noopener">{h(v["titolo"])}</a> · {h(v["nome"])}: {h(v["testo"])}</li>' for v in voci)
    return f'<aside class="aff"><h2>Strumenti per la partita IVA</h2><ul>{righe}</ul>{MON.nota_trasparenza("it")}</aside>'


# ---------------------------------------------------------------- home e indice di ricerca
def volume_mestiere(m):
    return sum(VOL["frasi"][f]["volume"] for f in m["frasi"] if f in VOL["frasi"])


MESTIERI_PUBBLICATI = [m for m in MES if volume_mestiere(m) > 0]


def _volumi_misurati():
    """Frase -> volume mensile misurato (misura del 13/11: frasi cercate e frasi simili restituite dallo strumento; poi quella del 12/11)."""
    out = {}
    for f, v in VOLA["frasi"].items():
        if v.get("volume") is not None:
            out[f] = v["volume"]
    for v in VOLA["frasi"].values():
        for f, n in (v.get("simili") or {}).items():
            out.setdefault(f, n)
    for f, v in VOL["frasi"].items():
        out.setdefault(f, v["volume"])
    return out


VOLUMI_MISURATI = _volumi_misurati()


def volume_attivita(a):
    """Volume di una pagina: la frase misurata più cercata tra le sue (le varianti vicine non si sommano: Google Ads le conta insieme)."""
    return max((VOLUMI_MISURATI.get(f, 0) or 0 for f in a["frasi"]), default=0)


ATTIVITA = [a for a in ATT if volume_attivita(a) >= MIN_VOLUME_ATTIVITA]


GUIDE_RICERCA = [  # pagine guida nella ricerca: titolo, indirizzo, parole che le fanno trovare
    ("Cosa cambia con ATECO 2025", "/cosa-cambia-ateco-2025/", "nuovi codici cosa cambia variazione cambiato cambio 2025 date"),
    ("Da ATECO 2022 a ATECO 2025", "/da-ateco-2022-a-2025/", "vecchio vecchi conversione corrispondenza raccordo tabella 2022"),
    ("Coefficienti del forfettario", "/coefficienti-redditivita-forfettario/", "coefficiente coefficienti redditività redditivita forfettario forfetario percentuale"),
]


def indice_ricerca():
    voci = [["Guida", t, u, "p", "", w] for t, u, w in GUIDE_RICERCA]
    voci += [["Guida", f"Codice ATECO {m['nome']}", f"/{m['slug']}/", "p", "", " ".join(m["frasi"]) + " " + m["nome"]] for m in MESTIERI_PUBBLICATI]
    voci += [["Guida", maiuscola(a["h1"]), f"/{a['slug']}/", "p", "", " ".join(a["frasi"]) + " " + a["nome"]] for a in ATTIVITA]
    voci.append(["Guida", "Codice ATECO per attività: tutte le guide", "/codice-ateco-per/", "p", "", "attività mestiere professione guide"])
    for c in ORDINE:
        v = C[c]
        # parole delle note di inclusione (senza ripetizioni e senza quelle del titolo): servono a trovare «pizzeria» in 56.11.11
        tit = set(re.findall(r"\w{4,}", v["it"].lower()))
        parole = []
        for w in re.findall(r"\w{4,}", " ".join(n["it"] for n in v["note"] if n["t"] in (1, 2, 5)).lower()):
            if w not in tit and w not in parole:
                parole.append(w)
        voci.append([c, v["it"], url_di(c), "25", "", " ".join(parole)[:400]])
    for c22, o in sorted(OP.items(), key=lambda kv: kv[0]):
        if o["l"] < 4 or not o["rap"]:
            continue
        voci.append([c22, o["t22"], f"/da-ateco-2022-a-2025/#v-{c22}" if o["l"] == 6 else url_di(o["rap"]), "22", o["rap"], ""])
    return json.dumps(voci, ensure_ascii=False, separators=(",", ":"))


INDICE = indice_ricerca()
INDICE_FILE = f"indice.{_impronta(INDICE)}.json"


def home():
    rim = Rimandi()
    form = (f'<form class="cerca" role="search" id="cerca" action="/" onsubmit="return false"><label class="sr" for="q" hidden>Cerca un codice ATECO</label>'
            f'<input id="q" type="search" data-cerca data-indice="/assets/{INDICE_FILE}" placeholder="Attività o codice: ristorante, software, 62.10…" autocomplete="off"></form>'
            '<ul class="risultati" data-risultati hidden></ul>')
    testata = banda("Classificazione Istat ATECO 2025", "Trova il tuo codice ATECO 2025",
                    f"Cerca per attività, per codice o con il <strong>vecchio codice ATECO 2022</strong>: titolo ufficiale, cosa comprende ed esclude, "
                    "corrispondenze e coefficiente del forfettario.", form, icona="search")
    corpo = (f'<div class="card pull cifre"><div class="cifra main"><b>{NUM["n_6"]}</b><span>sottocategorie ATECO 2025 (codici a 6 cifre)</span></div>'
             f'<div class="cifra"><b>{NUM["n_4"]}</b><span>classi, una pagina ciascuna</span></div>'
             f'<div class="cifra"><b>{NUM["n22_6"]}</b><span>vecchi codici ATECO 2022 con il codice nuovo</span></div>'
             f'<div class="cifra"><b>9</b><span>gruppi di coefficienti del forfettario</span></div>'
             f'<p class="asof">{ico("check")}ATECO 2025 in vigore dal 1° gennaio 2025, adottata dal 1° aprile 2025. Tavole di raccordo aggiornamento 2026 '
             f'(Istat, pagina aggiornata il {FJ["pagine"]["istat_ateco"].get("data_pagina") or "—"}).</p></div>')
    corpo += '<h2 id="utili">Guide</h2><ul class="griglia">'
    utili = [("/cosa-cambia-ateco-2025/", "Cosa cambia con ATECO 2025", "Date, cosa fare, chi riclassifica, come cambiare codice."),
             ("/da-ateco-2022-a-2025/", "Da ATECO 2022 a ATECO 2025", f"Il codice nuovo per ognuno dei {NUM['n22_6']} vecchi codici."),
             ("/coefficienti-redditivita-forfettario/", "Coefficienti del forfettario", "Le 9 percentuali di legge e quale codice conta.")]
    utili += [(f"/{m['slug']}/", f"Codice ATECO {m['nome']}", m["descrizione"][:90] + "…") for m in MESTIERI_PUBBLICATI]
    corpo += "".join(f'<li><a href="{u}"><b>{h(t)}</b><span>{h(s)}</span></a></li>' for u, t, s in utili) + "</ul>"
    piu = sorted(ATTIVITA, key=lambda a: -volume_attivita(a))[:8]
    corpo += ('<h2 id="per-attivita">Codice ATECO per attività</h2><p class="small">Le attività più cercate, con le note Istat che portano a ogni codice. '
              f'<a href="/codice-ateco-per/">Tutte le {len(ATTIVITA) + len(MESTIERI_PUBBLICATI)} guide</a>.</p><ul class="griglia">'
              + "".join(f'<li><a href="/{a["slug"]}/"><b>{h(maiuscola(a["h1"]))}</b><span>{h(accorcia(a["descrizione"], 90))}</span></a></li>' for a in piu)
              + "</ul>")
    corpo += '<h2 id="sezioni">Le 22 sezioni di ATECO 2025</h2><ul class="albero">'
    for s in SEZIONI:
        corpo += (f'<li><a class="cod" href="{url_di(s)}">Sezione {s}</a><span>{h(C[s]["it"][0] + C[s]["it"][1:].lower())}</span>'
                  f'<span class="mini">Divisioni {", ".join(FIGLI[s][:1] + (["…", FIGLI[s][-1]] if len(FIGLI[s]) > 1 else []))}</span></li>')
    corpo += "</ul>"
    corpo += ('<h2 id="come-si-legge">Come si legge un codice ATECO</h2><div class="testo">'
              f'<p>ATECO 2025 è una classificazione ad albero: una lettera per la sezione, poi fino a sei cifre. Esempio con '
              f'{link_cod("96.21.00")} «{h(C["96.21.00"]["it"])}»:{rim.ref("istat_ateco")}</p><ul>'
              f'<li><strong>{antenato("96", 1)}</strong>: sezione «{h(C[antenato("96", 1)]["it"].capitalize())}»</li>'
              f'<li><strong>96</strong>: divisione «{h(C["96"]["it"])}»</li><li><strong>96.2</strong>: gruppo «{h(C["96.2"]["it"])}»</li>'
              f'<li><strong>96.21</strong>: classe; <strong>96.21.0</strong>: categoria; <strong>96.21.00</strong>: sottocategoria, il codice a sei cifre dei moduli.</li></ul>'
              '<p>Le note Istat dicono cosa è incluso («Comprende»), cosa è incluso anche se non ovvio («Comprende anche») e cosa sta in un altro codice '
              '(«Non comprende», con il rimando). Istat avverte che gli esempi delle note di inclusione non sono esaustivi.</p></div>')
    voci = faq_pagina("home", rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/", "inLanguage": "it"}]
    if f_ld:
        ld.append(f_ld)
    pagina("", "Codici ATECO 2025: cerca il codice, elenco e vecchi codici",
           "Cerca il codice ATECO 2025 per attività o numero: titoli ufficiali Istat, cosa include ed esclude, vecchio codice 2022 e coefficiente del forfettario.",
           corpo, testata.replace("{bc}", ""), jsonld=ld)


# ---------------------------------------------------------------- da ATECO 2022 a ATECO 2025
def da_2022():
    rim = Rimandi()
    righe, attr = [], []
    for c22 in sorted(OP6):
        o = OP6[c22]
        tutte = [r["c25"] for r in RAC22[c22] if len(r["c25"]) == 8]
        rap = link_cod(o["rap"]) if o["rap"] else "—"
        cam = f'<br><span class="mini">Camere di commercio: {link_cod(o["cam"])}</span>' if o["cam"] and o["cam"] != o["rap"] else ""
        if len(tutte) > 1:
            lista = "".join(f'<li>{link_cod(x)} {h(accorcia(C[x]["it"], 70))}</li>' for x in tutte)
            tut = f'<details class="tutte"><summary>{len(tutte)} codici possibili</summary><ul>{lista}</ul></details>'
        else:
            tut = "1 (uno a uno)" if o["tipo"] == "1-1" else "1"
        righe.append([f'<span class="cod">{c22}</span>', h(o["t22"]), rap + cam, tut])
        attr.append(f' id="v-{c22}"')
    tab = tabella(["ATECO 2022", "Titolo 2022", "Codice ATECO 2025 rappresentativo", "Corrispondenze nella tavola"], righe, attr=attr, resp="resp7")
    corpo = (f'<div class="card pull"><p style="margin:0"><strong>Per ogni vecchio codice ATECO 2022 a sei cifre: il codice ATECO 2025 rappresentativo '
             f'della tabella operativa Istat</strong> (con quello delle Camere di commercio, se diverso) e tutte le corrispondenze possibili della tavola di '
             f'raccordo, aggiornamento 2026.{rim.ref(["operativa", "raccordo"])}</p></div>')
    corpo += nota("La tabella operativa sceglie un solo codice anche quando il vecchio codice si divide in più codici nuovi: Istat avverte che «questa "
                  f"semplificazione implica inevitabilmente una perdita di informazioni».{rim.ref('istat_ateco')} Nei casi con più corrispondenze leggi le "
                  f"note dei codici possibili e {FRASE_FISSA}.", "info")
    corpo += (f'<div data-tabella><div class="filtri"><input type="search" data-filtro placeholder="Vecchio codice o parola: 47.91.10, parrucchiere…" '
              f'aria-label="Filtra i codici"></div><p class="conteggio" data-conteggio></p>{tab}<p class="vuoto-ricerca" data-vuoto hidden>Nessun codice trovato.</p>'
              '<p class="altre" data-altre hidden><button type="button" class="btn sec" data-altre-piu>Mostra altri 100</button>'
              '<button type="button" class="btn sec" data-altre-tutte>Mostra tutti</button></p></div>')
    corpo += (f'<h2 id="numeri">I numeri del passaggio</h2><div class="testo"><ul><li>{NUM["n22_11"]} codici ATECO 2022 hanno una corrispondenza uno a uno.</li>'
              f'<li>{NUM["n22_n1"]} confluiscono con altri in un solo codice ATECO 2025.</li><li>{NUM["n22_c"]} si dividono tra più codici ATECO 2025 '
              f'(ricodifica complessa).</li></ul></div>')
    voci = faq_pagina("da-ateco-2022-a-2025", rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    testata = banda("Tabella di conversione", "Da ATECO 2022 a ATECO 2025: il codice nuovo",
                    f"Scrivi il vecchio codice o una parola: {NUM['n22_6']} sottocategorie ATECO 2022 con il codice ATECO 2025 della tabella operativa Istat.", icona="swap")
    pagina("da-ateco-2022-a-2025/", "Da ATECO 2022 a ATECO 2025: tabella di conversione",
           f"Il nuovo codice ATECO 2025 per ognuno dei {NUM['n22_6']} vecchi codici ATECO 2022: tabella operativa e tavola di raccordo Istat, aggiornamento 2026.",
           corpo, testata, briciole=[("Home", ""), ("Da ATECO 2022 a 2025", "da-ateco-2022-a-2025/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- cosa cambia
def cosa_cambia():
    rim = Rimandi()
    nuovi = [c for c in ORDINE if C[c]["l"] == 6 and not vecchi_di(c)]
    divisi = sorted(OP6, key=lambda c: -len([r for r in RAC22[c] if len(r["c25"]) == 8]))[:10]
    sez22 = sum(1 for v in OP.values() if v["l"] == 1)
    corpo = (f'<div class="card pull cifre"><div class="cifra main"><b>1/1/2025</b><span>ATECO 2025 in vigore</span></div>'
             f'<div class="cifra"><b>1/4/2025</b><span>adottata da Istat, Camere di commercio e Agenzia delle entrate</span></div>'
             f'<div class="cifra"><b>{NUM["n_1"]}</b><span>sezioni (erano {sez22} in ATECO 2022)</span></div>'
             f'<div class="cifra"><b>2026</b><span>aggiornamento: cambiano solo le corrispondenze</span></div></div>')
    corpo += ('<h2 id="date">Le date</h2><div class="testo"><ul>'
              f'<li>ATECO 2025 è entrata in vigore il <strong>1° gennaio 2025</strong> e sostituisce ATECO 2007 – aggiornamento 2022. È coerente con la '
              f'classificazione europea NACE Rev. 2.1.{rim.ref(["istat_ateco", "risoluzione_24e"])}</li>'
              f'<li>È adottata operativamente dal <strong>1° aprile 2025</strong> da Istat, sistema camerale e Agenzia delle entrate; prima di quella data '
              f'a imprese e professionisti non era richiesta alcuna azione.{rim.ref("nota_congiunta")}</li>'
              f'<li>L\'<strong>aggiornamento 2026</strong> non ha cambiato struttura, livelli o descrizioni: ha aggiornato solo le corrispondenze con ATECO 2022 '
              f'(tavola di raccordo e tabella operativa).{rim.ref("istat_ateco")}</li></ul></div>')
    corpo += ('<h2 id="cosa-fare">Cosa devono fare imprese e professionisti</h2><div class="testo"><ul>'
              f'<li><strong>Nessuna dichiarazione obbligatoria.</strong> L\'adozione di ATECO 2025 non comporta l\'obbligo di presentare la dichiarazione di '
              f'variazione dati.{rim.ref("risoluzione_24e")}</li>'
              f'<li><strong>Atti e dichiarazioni.</strong> Dal 1° aprile 2025 i nuovi codici si usano negli atti e nelle dichiarazioni da presentare '
              f'all\'Agenzia delle entrate.{rim.ref("risoluzione_24e")}</li>'
              f'<li><strong>Registro delle imprese.</strong> Le Camere di commercio eseguono la riclassificazione d\'ufficio a partire dal 1° aprile 2025; per un periodo '
              f'transitorio la visura camerale riporta sia i nuovi codici sia quelli precedenti.{rim.ref("nota_congiunta")}</li>'
              f'<li><strong>Controllare il proprio codice.</strong> Nell\'area riservata dell\'Agenzia delle entrate, in «Cassetto fiscale – Consultazioni – '
              f'Anagrafica», si vedono i codici prevalente e secondari registrati.{rim.ref("risoluzione_24e")}</li>'
              f'<li><strong>Se il nuovo codice non descrive bene l\'attività</strong>, la variazione si comunica con ComUnica (imprese iscritte al Registro) '
              f'o con i modelli dell\'Agenzia delle entrate (AA9/12 per imprese individuali e professionisti, AA7/10 per società ed enti).{rim.ref("nota_congiunta")} '
              f'Per la scelta del codice, {FRASE_FISSA}.</li></ul></div>')
    corpo += ('<h2 id="forfettario">Forfettario: il coefficiente segue ancora ATECO 2007</h2><div class="testo">'
              f'<p>Fino all\'approvazione di nuovi coefficienti di redditività basati su ATECO 2025, chi è nel regime forfetario continua a usare il coefficiente '
              f'della tabella di legge «individuato sulla base del codice corrispondente all\'attività esercitata secondo la classificazione ATECO 2007».'
              f'{rim.ref("dlgs81_art1")} La regola è ripresa dall\'art. 235, comma 6, del testo unico delle imposte sui redditi, che si applica dal '
              f'1° gennaio 2027.{rim.ref(["tuir_art235", "tuir_art377"])} <a href="/coefficienti-redditivita-forfettario/">Tabella dei coefficienti</a>.</p></div>')
    rr = []
    for c22 in divisi:
        n = len([r for r in RAC22[c22] if len(r["c25"]) == 8])
        rr.append([f'<a class="cod" href="/da-ateco-2022-a-2025/#v-{c22}">{c22}</a>', h(OP[c22]["t22"]), num(n)])
    corpo += (f'<h2 id="piu-divisi">I vecchi codici che si dividono di più</h2><p class="small">Numero di codici ATECO 2025 collegati nella tavola di raccordo '
              f'(sesto livello).{rim.ref("raccordo")}</p>' + tabella(["ATECO 2022", "Titolo", "Codici 2025"], rr, num_=[2]))
    corpo += (f'<p>Un caso tipico è il commercio via internet: il vecchio 47.91.10 si divide in {NUM["n_ecom"]} codici, perché ora il commercio al '
              f'dettaglio si classifica per prodotto venduto e non per canale. <a href="/codice-ateco-e-commerce/">Codice ATECO per l\'e-commerce</a>.</p>')
    if nuovi:
        corpo += (f'<h2 id="nuovi">Codici senza un vecchio corrispondente</h2><p>Nella tavola di raccordo {len(nuovi)} '
                  f'{"sottocategoria non ha" if len(nuovi) == 1 else "sottocategorie non hanno"} nessun codice ATECO 2022 corrispondente: '
                  + ", ".join(f'{link_cod(c)} «{h(C[c]["it"])}»' for c in nuovi) + f'.{rim.ref("raccordo")}</p>')
    corpo += box_affiliati()
    voci = faq_pagina("cosa-cambia", rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    testata = banda("Nuova classificazione", "Codici ATECO 2025: cosa cambia e cosa fare",
                    "Le date, chi riclassifica i codici, quando serve comunicare una variazione e cosa resta uguale per il forfettario.", icona="calendar")
    pagina("cosa-cambia-ateco-2025/", "Nuovi codici ATECO 2025: cosa cambia e cosa fare",
           "ATECO 2025 in vigore dal 1° gennaio e adottata dal 1° aprile 2025: riclassificazione d'ufficio, nessuna variazione obbligatoria, forfettario.",
           corpo, testata, briciole=[("Home", ""), ("Cosa cambia", "cosa-cambia-ateco-2025/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- coefficienti
def coefficienti():
    rim = Rimandi()
    rr = [[f'<b>{t["coefficiente"]}%</b>', h(t["gruppo"]), h(t["codici_ateco_2007"])] for _, t in sorted(TABCO.items(), key=lambda kv: int(kv[0]))]
    corpo = (f'<div class="card pull"><p style="margin:0"><strong>Il coefficiente si sceglie ancora con il codice ATECO 2007</strong>, non con quello 2025: '
             f'«fino alla approvazione dei nuovi coefficienti di redditività elaborati sulla base della classificazione delle attività economiche ATECO 2025».'
             f'{rim.ref("dlgs81_art1")} Lo ripetono le istruzioni dell\'Agenzia delle entrate al modello Redditi Persone fisiche 2026 (quadro LM): nel '
             f'rigo LM21 si indica il codice ATECO 2025 dell\'attività, ma il coefficiente resta quello «individuato sulla base del codice corrispondente '
             f'all\'attività esercitata secondo la classificazione ATECO 2007».{rim.ref("istruzioni_lm")}</p></div>')
    corpo += (f'<h2 id="tabella">La tabella di legge</h2><p class="small">Allegato 4 della legge 23 dicembre 2014, n. 190 (testo vigente); identico '
              f'all\'allegato D del testo unico delle imposte sui redditi (D.Lgs. 117/2026), che si applica dal 1° gennaio 2027.'
              f'{rim.ref(["l190_all4", "tuir_allD", "tuir_art377"])}</p>'
              + tabella(["Coefficiente", "Gruppo di settore", "Codici attività ATECO 2007"], rr))
    corpo += ('<h2 id="come-si-usa">Come si usa</h2><div class="testo">'
              f'<p>Il reddito imponibile del forfetario si calcola applicando ai ricavi o ai compensi percepiti il coefficiente del gruppo dell\'attività; sul reddito '
              f'così ottenuto si applica l\'imposta sostitutiva.{rim.ref("tuir_art235")}</p>'
              '<p>Le divisioni e i gruppi della tabella sono di ATECO 2007, che con l\'aggiornamento 2022 non ha cambiato divisioni, gruppi e classi: per questo '
              'nelle pagine dei codici il coefficiente è ricavato dai codici ATECO 2022 che la tavola di raccordo Istat collega a ogni sottocategoria '
              f'ATECO 2025.{rim.ref("raccordo")} Quando i vecchi codici cadono in gruppi diversi, la pagina lo dice e mostra i coefficienti possibili: conta il '
              f'codice ATECO 2007 della tua attività, quindi {FRASE_FISSA}.</p></div>')
    # tabella per divisione ATECO 2025
    rr = []
    for d in DIVISIONI:
        subs = sottocategorie(d)
        cnt = Counter(g for s in subs for g in gruppi_coeff(s))
        if not cnt:
            continue
        parti = ", ".join(f'{coeff_txt(g)} ({n})' for g, n in sorted(cnt.items(), key=lambda kv: -kv[1]))
        rr.append([link_cod(d), h(accorcia(C[d]["it"], 80)), parti])
    corpo += (f'<h2 id="per-divisione">Coefficienti per divisione ATECO 2025</h2><p class="small">Per ogni divisione: i coefficienti dei vecchi codici collegati '
              f'alle sue sottocategorie e, tra parentesi, quante sottocategorie li hanno.{rim.ref(["raccordo", "l190_all4"])}</p>'
              + tabella(["Divisione", "Titolo", "Coefficienti (sottocategorie)"], rr, resp="resp7"))
    corpo += box_affiliati()
    voci = faq_pagina("coefficienti", rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    testata = banda("Regime forfetario", "Coefficienti di redditività del forfettario per codice ATECO",
                    "Le nove percentuali di legge, quale codice conta dopo ATECO 2025 e i coefficienti per ogni divisione.", icona="percent")
    pagina("coefficienti-redditivita-forfettario/", "Coefficienti di redditività forfettario per codice ATECO",
           "Coefficienti di redditività del forfettario: tabella di legge (allegato 4 L. 190/2014), regola del codice ATECO 2007 e coefficienti per divisione 2025.",
           corpo, testata, briciole=[("Home", ""), ("Coefficienti del forfettario", "coefficienti-redditivita-forfettario/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- mestieri

def pagina_mestiere(m):
    rim = Rimandi()
    corpo = f'<div class="card pull"><p style="margin:0">{h(m["intro"])}{rim.ref(["struttura", "raccordo"])}</p></div>'
    controlla_titoli_citati(m["intro"], m["slug"])
    if m.get("tipo") == "ecommerce":
        n47 = C["47"]["note"]
        principio = [n for n in n47 if n["t"] == 1 and n["it"].startswith("La classificazione delle attività di commercio al dettaglio avviene")]
        marketplace = [n for n in n47 if n["t"] == 1 and n["it"].startswith("Le attività di servizi di intermediazione per il commercio al dettaglio")]
        digitale = [n for n in n47 if n["t"] == 3 and "beni digitali" in n["it"]]
        corpo += '<h2 id="regola">La regola di Istat</h2>'
        for n in principio + marketplace:
            corpo += f'<blockquote class="legge">{h(n["it"])}<cite>Note esplicative Istat, divisione 47{rim.ref("note")}</cite></blockquote>'
        for n in digitale:
            corpo += f'<p>Esclusione nella divisione 47: «{linkifica(n["it"], n["rif"])}».{rim.ref("note")}</p>'
        righe = [r for r in RAC22["47.91.10"] if len(r["c25"]) == 8]
        rr = [[link_cod(r["c25"]), h(C[r["c25"]]["it"]), comune_html(r["comune"])] for r in righe]
        corpo += (f'<h2 id="corrispondenze">Dove va oggi la vendita online: le {len(righe)} corrispondenze di 47.91.10</h2><p class="small">Tavola di raccordo '
                  f'Istat ATECO 2025 – ATECO 2022, aggiornamento 2026: ogni riga è un codice ATECO 2025 con la parte di vendita via Internet che riceve dal vecchio '
                  f'47.91.10.{rim.ref("raccordo")}</p>' + tabella(["ATECO 2025", "Titolo", "Contenuto in comune"], rr, resp="resp7"))
        o = OP["47.91.10"]
        corpo += nota(f'La tabella operativa di riclassificazione porta 47.91.10 al codice di livello superiore {link_cod(o["rap"])} «{h(C[o["rap"]]["it"])}»: '
                      f'è un codice di gruppo usato per le riclassificazioni massive, non una sottocategoria da indicare nei moduli.{rim.ref("operativa")}', "info")
        corpo += '<h2 id="marketplace">Se gestisci un marketplace</h2>'
        for c in m["vicini"]:
            corpo += voce_sottocategoria(c, rim, "h3")
        corpo += ('<h2 id="forfettario">Forfettario</h2><p>Per il coefficiente conta il codice ATECO 2007 dell\'attività: il vecchio 47.91.10 è nella classe 47.9, '
                  f'gruppo {GRUPPO22["47.91.10"]} «{h(TABCO[str(GRUPPO22["47.91.10"])]["gruppo"])}», coefficiente <b>{coeff_txt(GRUPPO22["47.91.10"])}</b>.'
                  f'{rim.ref(["l190_all4", "dlgs81_art1"])}</p>')
    else:
        corpo += f'<h2 id="codice">Il codice ATECO 2025</h2>'
        for c in m["codici"]:
            cl = antenato(c, 4)
            if C[cl]["note"] and cl not in [antenato(x, 4) for x in m["codici"][:m["codici"].index(c)]]:
                corpo += f'<h3>La classe {cl} «{h(C[cl]["it"])}»</h3>' + note_html(cl, rim)
            corpo += voce_sottocategoria(c, rim, "h3")
        corpo += '<h2 id="vecchio">Il vecchio codice ATECO 2022</h2>'
        rr = []
        for c22 in m["vecchi"]:
            for r in RAC22[c22]:
                if len(r["c25"]) == 8:
                    rr.append([f'<a class="cod" href="/da-ateco-2022-a-2025/#v-{c22}">{c22}</a>', h(OP[c22]["t22"]), link_cod(r["c25"]), comune_html(r["comune"])])
        corpo += (f'<p class="small">Tavola di raccordo Istat, aggiornamento 2026.{rim.ref("raccordo")}</p>'
                  + tabella(["ATECO 2022", "Titolo 2022", "ATECO 2025", "Contenuto in comune"], rr, resp="resp7"))
        corpo += '<h2 id="da-non-confondere">Codici vicini da non confondere</h2><ul class="albero">'
        for c in m["vicini"]:
            corpo += f'<li>{link_cod(c)}<span>{h(C[c]["it"])}</span></li>'
        corpo += "</ul>"
    corpo += nota(f"Il codice va scelto sull'attività svolta davvero: le note Istat danno esempi, non un elenco completo. Prima di comunicarlo, {FRASE_FISSA}.",
                  "info", "alert")
    corpo += box_affiliati()
    voci = faq_pagina(m["slug"], rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html + rim.elenco()
    testata = banda("Codice ATECO per mestiere", m["h1"], h(m["descrizione"]), icona="tag")
    pagina(m["slug"] + "/", m["titolo"], m["descrizione"], corpo, testata,
           briciole=[("Home", ""), (m["h1"], m["slug"] + "/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- pagine «Codice ATECO per …» (13/11/2026)
INDICIZZA_ATT = {}  # percorso -> True/False (misura_attivita)
MISURA_ATT = {}
_SEGNAPOSTO = re.compile(r"\{(c|t|ct|v|perc|t22|d22):([\dA-Z][\d.]*)\}")


def vecchi_codici(c):
    return sorted({r["c22"] for r in vecchi_di(c)})


def percentuali(c):
    p = sorted({TABCO[str(g)]["coefficiente"] for g in gruppi_coeff(c)})
    return " o ".join(f"{x}%" for x in p) if p else "nessun coefficiente ricavabile"


def riempi_att(testo, html=True, dove=""):
    """Segnaposto nei testi nostri: {c:X} codice (link), {t:X} «titolo ufficiale», {ct:X} codice e titolo, {v:X} vecchi codici 2022,
    {perc:X} coefficienti ricavati dai vecchi codici. I titoli e i numeri vengono sempre dai dati, mai scritti a mano."""
    def sost(m):
        k, c = m.group(1), m.group(2)
        if k in ("t22", "d22"):
            if c not in OP:
                raise SystemExit(f"{dove}: {c} non è un codice ATECO 2022")
            if k == "t22":
                return h(f"«{OP[c]['t22']}»") if html else f"«{OP[c]['t22']}»"
            dest = sorted({r["c25"] for r in RAC22[c] if len(r["c25"]) == 8})
            return "; ".join(f"{link_cod(x) if html else x} {h('«' + C[x]['it'] + '»') if html else '«' + C[x]['it'] + '»'}" for x in dest)
        if c not in C:
            raise SystemExit(f"{dove}: {c} non è un codice ATECO 2025")
        tit = f"«{C[c]['it']}»"
        cod = link_cod(c) if html else c
        if k == "c":
            return cod
        if k == "t":
            return h(tit) if html else tit
        if k == "ct":
            return f"{cod} {h(tit) if html else tit}"
        if k == "v":
            return ", ".join(vecchi_codici(c)) or "nessuno"
        return percentuali(c)
    if html:
        parti = _SEGNAPOSTO.split(testo)
        out = ""
        for i in range(0, len(parti), 3):
            out += h(parti[i])
            if i + 2 < len(parti):
                out += sost(re.match(_SEGNAPOSTO, "{" + parti[i + 1] + ":" + parti[i + 2] + "}"))
        return out
    return _SEGNAPOSTO.sub(sost, testo)


def riga_istat(c, testo, con_link=False, rif=None):
    """Riga ufficiale citata tale e quale (nota Istat o titolo del codice c); verifica.py la ritrova nel file Istat."""
    corpo = linkifica(testo, rif) if con_link else h(testo)
    return f'<q class="ni" data-c="{c}">{corpo}</q>'


def risolvi_riga(c, pref, dove):
    if pref == "=titolo":
        return C[c]["it"]
    trovate = [n["it"] for n in C[c]["note"] if n["it"].startswith(pref) and n["t"] != 3] or [n["it"] for n in C[c]["note"] if n["it"].startswith(pref)]
    if len(trovate) != 1:
        raise SystemExit(f"{dove}: {len(trovate)} note di {c} iniziano con «{pref}»")
    return trovate[0]


def righe_scelte(a):
    """{codice: righe ufficiali} della tabella delle scelte: scelte a mano (inizio della nota o =titolo) o le note di inclusione del codice."""
    out = {}
    for c in a["evidenza"]:
        if c not in C or C[c]["l"] < 4:
            raise SystemExit(f"{a['slug']}: {c} non è un codice ATECO 2025 di classe o sottocategoria")
        scelte = a.get("scelte", {}).get(c)
        if scelte:
            out[c] = [risolvi_riga(c, p, a["slug"]) for p in scelte]
            continue
        inc = [n["it"] for n in C[c]["note"] if n["t"] in (2, 5) and not n["it"].rstrip().endswith(":")]
        out[c] = inc[:MAX_RIGHE_CODICE] or [C[c]["it"]]
    return out


def esclusioni(a):
    """Note «Non comprende» dei codici in evidenza e delle loro classi e categorie: [(codice della nota, nota)], senza doppioni."""
    visti, out = {}, []
    for i, c in enumerate(a["evidenza"]):
        # classe e categoria solo per i due codici principali: le esclusioni lunghe delle classi vicine renderebbero le guide simili tra loro
        catena = [c] + ([antenato(c, l) for l in (5, 4) if C[c]["l"] > l] if i < 2 else [])
        for x in catena:
            for n in C[x]["note"]:
                if n["t"] != 3 or not n["rif"]:
                    continue
                chiave = n["it"].split(", cfr.")[0].lower()
                if chiave in visti:
                    continue
                if a.get("escludi_rx") and not re.search(a["escludi_rx"], n["it"], re.I):
                    continue
                visti[chiave] = True
                out.append((x, n))
    return out[:a.get("max_esclusioni", MAX_ESCLUSIONI)]


def faq_attivita(a, rim):
    voci = []
    for x in FAQ:
        if x["pagina"] != a["slug"]:
            continue
        if not VOLUMI_MISURATI.get(x["ricerca"]):
            raise SystemExit(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non ha un volume misurato")
        risp = riempi_att(x["a"], html=False, dove=f"FAQ {a['slug']}")
        controlla_titoli_citati(risp, f"FAQ {a['slug']}")
        voci.append((x["q"], risp, rim.ref(x["fonti"])))
    return voci


def pagina_attivita(a):
    rim = Rimandi()
    dove = a["slug"]
    intro = riempi_att(a["intro"], dove=dove)
    controlla_titoli_citati(riempi_att(a["intro"], html=False, dove=dove), dove)
    fonti_intro = a.get("fonti_intro", ["struttura", "note"])  # fonti delle frasi dell'introduzione (es. «operativa» se cita la tabella operativa)
    corpo = f'<div class="card pull testo">' + "".join(f"<p>{p}</p>" for p in intro.split("\n\n")) + f'<p class="mini">Titoli e note: Istat ATECO 2025{rim.ref(fonti_intro)}</p></div>'
    scelte = righe_scelte(a)
    rr = [["<br>".join(riga_istat(c, r) for r in righe), link_cod(codice_principale(c) if C[c]["l"] == 4 else c),
           '<span class="mini">il titolo ufficiale, citato a sinistra</span>' if righe == [C[c]["it"]] else h(C[c]["it"])]
          for c, righe in scelte.items()]
    corpo += ('<h2 id="quale-codice">Quale codice: cosa dicono le note Istat</h2><p class="small">Nella prima colonna le righe delle note '
              'esplicative Istat (o il titolo ufficiale) del codice accanto, citate parola per parola: se l\'attività svolta davvero è quella, Istat la '
              f'classifica lì.{rim.ref("note")}</p>' + tabella(["Se l'attività è…", "Codice ATECO 2025", "Titolo ufficiale"], rr, resp="resp7"))
    if a.get("citazioni"):
        corpo += '<h2 id="regola">La regola di Istat</h2>'
        for c, pref in a["citazioni"]:
            corpo += (f'<blockquote class="legge">{riga_istat(c, risolvi_riga(c, pref, dove))}<cite>Note esplicative Istat, '
                      f'{LIVELLI[C[c]["l"]]} {link_cod(c)}{rim.ref("note")}</cite></blockquote>')
    escl = esclusioni(a)
    if escl:
        rr = [[riga_istat(x, n["it"], True, n["rif"]), f'{link_cod(x)}'] for x, n in escl]
        corpo += ('<h2 id="altri-codici">Cosa Istat mette in un altro codice</h2><p class="small">Note «Non comprende» dei codici qui sopra (o della '
                  f'loro classe): l\'attività descritta non va in quel codice ma in quello dopo «cfr.».{rim.ref("note")}</p>'
                  + tabella(["Nota di esclusione Istat", "Nota del codice"], rr, resp="resp7"))
    sei = [c for c in a["evidenza"] if C[c]["l"] == 6]
    if sei:
        corpo += ('<h2 id="forfettario">Coefficiente del forfettario dei codici indicati</h2><p class="small">La classificazione ATECO non contiene '
                  'coefficienti: sono nell\'allegato 4 della legge 190/2014, che usa i codici ATECO 2007. Per ogni codice la percentuale è ricavata da noi '
                  'dai vecchi codici collegati nella tavola di raccordo Istat, come nelle pagine dei codici.</p>')
        for c in sei:
            corpo += (f'<section class="voce" id="k-{c}"><h3><span class="chip-cod">{c}</span> <a href="{url_di(c)}">{h(C[c]["it"])}</a></h3>'
                      f'{blocco_coeff(c, rim)}</section>')
        vecchi = sorted({c22 for c in sei for c22 in vecchi_codici(c)})
        rr = []
        for c22 in vecchi:
            dest = [r for r in RAC22[c22] if len(r["c25"]) == 8]
            for r in dest:
                if r["c25"] in sei:
                    rr.append([f'<a class="cod" href="/da-ateco-2022-a-2025/#v-{c22}">{c22}</a>', h(OP[c22]["t22"]), link_cod(r["c25"]), comune_html(r["comune"])])
            altri = [r["c25"] for r in dest if r["c25"] not in sei]
            if altri:  # le altre destinazioni del vecchio codice: solo il numero, l'elenco è nella tabella 2022 → 2025
                rr.append([f'<a class="cod" href="/da-ateco-2022-a-2025/#v-{c22}">{c22}</a>', h(OP[c22]["t22"]),
                           f'<a href="/da-ateco-2022-a-2025/#v-{c22}">{"un altro codice" if len(altri) == 1 else f"altri {len(altri)} codici"}</a>', "—"])
        if rr:
            corpo += (f'<h2 id="vecchi-codici">Dai vecchi codici ATECO 2022 ai codici 2025</h2><p class="small">Tavola di raccordo Istat ATECO 2025 – '
                      f'ATECO 2022, aggiornamento 2026: per ogni vecchio codice, i codici indicati in questa guida in cui confluisce e quanti altri ne riceve una parte. ATECO 2022 è '
                      f'l\'aggiornamento 2022 di ATECO 2007.{rim.ref("raccordo")}</p>'
                      + tabella(["ATECO 2022", "Titolo 2022", "ATECO 2025", "Contenuto in comune (Istat)"], rr, resp="resp7"))
    corpo += nota(f"Il codice va scelto sull'attività svolta davvero: le note Istat danno esempi, non un elenco completo. Prima di comunicarlo, {FRASE_FISSA}.",
                  "info", "alert")
    corpo += box_affiliati()
    voci = faq_attivita(a, rim)
    f_html, f_ld = faq_html(voci)
    corpo += f_html
    pubblicate = {x["slug"]: maiuscola(x["h1"]) for x in ATTIVITA} | {m["slug"]: f"Codice ATECO {m['nome']}" for m in MESTIERI_PUBBLICATI}
    vicine = [f'<a href="/{s}/">{h(pubblicate[s])}</a>' for s in a.get("vedi", []) if s in pubblicate]
    corpo += ('<p class="small">' + (f'Guide vicine: {"; ".join(vicine)}. ' if vicine else "")
              + 'Tutte le attività: <a href="/codice-ateco-per/">codice ATECO per attività</a>.</p>' + rim.elenco())
    controlla_codici_attivita(dove, corpo)
    testata = banda("Codice ATECO per attività", maiuscola(a["h1"]), h(a["descrizione"]), icona="tag")
    pagina(a["slug"] + "/", a["titolo"], a["descrizione"], corpo, testata,
           briciole=[("Home", ""), ("Per attività", "codice-ateco-per/"), (maiuscola(a["h1"]), a["slug"] + "/")], jsonld=[f_ld] if f_ld else None,
           indicizza=INDICIZZA_ATT.get(a["slug"] + "/", True))


def controlla_codici_attivita(dove, corpo):
    """Ogni codice ATECO 2025 a 6 cifre della tabella delle scelte o del forfettario ha almeno una riga ufficiale citata nella pagina;
    ogni codice citato in un link esiste."""
    t = re.sub(r'<section class="fonti-box".*?</section>', " ", corpo, flags=re.S)
    for c in re.findall(r'href="/[\w-]+/#c-([\d.]+)"', t):
        if c not in C:
            raise SystemExit(f"{dove}: link a un codice inesistente {c}")
    citati = set(re.findall(r'<q class="ni" data-c="([\d.A-Z]+)">', t))
    for c in re.findall(r'<section class="voce" id="k-([\d.]+)">', t):
        if c not in citati:
            raise SystemExit(f"{dove}: {c} senza una riga Istat citata nella pagina")


GUIDE_DI = defaultdict(list)  # classe -> guide (pagine attività e mestieri) che indicano un suo codice


def _guide_di():
    tutte = [(m["slug"], f"Codice ATECO {m['nome']}", [*m["codici"], *(["47.91.10"] if m.get("tipo") == "ecommerce" else [])]) for m in MESTIERI_PUBBLICATI]
    tutte += [(a["slug"], maiuscola(a["h1"]), a["evidenza"]) for a in ATTIVITA]
    for slug, nome, cods in tutte:
        for cl in dict.fromkeys(antenato(c, 4) for c in cods if c in C and C[c]["l"] >= 4):
            if (slug, nome) not in GUIDE_DI[cl]:
                GUIDE_DI[cl].append((slug, nome))


_guide_di()


def blocco_guide(cl):
    """Link dalla pagina di classe alle guide per attività che indicano un suo codice (al massimo 3; non contano come testo della pagina)."""
    g = GUIDE_DI.get(cl, [])[:3]
    if not g:
        return ""
    return ('<section data-ripreso><h2 id="guide">Guide per attività che indicano questo codice</h2><ul>'
            + "".join(f'<li><a href="/{s}/">{h(n)}</a></li>' for s, n in g) + "</ul></section>")


def indice_attivita():
    rim = Rimandi()
    righe = []
    voci = [(a["slug"], maiuscola(a["nome"]), [c for c in a["evidenza"]], volume_attivita(a)) for a in ATTIVITA]
    voci += [(m["slug"], maiuscola(m["nome"]), m["codici"] or [], volume_mestiere(m)) for m in MESTIERI_PUBBLICATI]
    for slug, nome, cods, _ in sorted(voci, key=lambda x: x[1].lower()):
        if cods:
            c = codice_principale(cods[0]) if C[cods[0]]["l"] == 4 else cods[0]
            cod = f'{link_cod(c)} {h(C[c]["it"])}'
            if len(cods) > 1:
                cod += f'<small>{"e un altro codice" if len(cods) == 2 else f"e altri {len(cods) - 1} codici"} nella guida</small>'
        else:
            cod = "Dipende da cosa vendi: le corrispondenze del vecchio 47.91.10"
        righe.append([f'<a href="/{slug}/">{h(nome)}</a>', cod])
    corpo = ('<div class="card pull"><p style="margin:0">Guide per le attività che in Italia si cercano di più con «codice ATECO …»: '
             f'{len(voci)} attività, ognuna con almeno {MIN_VOLUME_ATTIVITA} ricerche al mese su Google misurate. Ogni guida cita parola per parola '
             f'le note esplicative Istat che portano a ogni codice, i vecchi codici collegati e il coefficiente del forfettario ricavato da noi.{rim.ref("note")}</p></div>')
    corpo += ('<h2 id="attivita">Attività e codici</h2><p class="small">Prima colonna: la guida. Seconda colonna: il primo codice indicato dalla guida '
              'con il suo titolo ufficiale, e quanti altri codici confronta.</p>' + tabella(["Attività", "Codici ATECO 2025"], righe, resp="resp7"))
    corpo += ('<h2 id="altre">L\'attività non c\'è?</h2><div class="testo"><p>Usa la <a href="/#cerca">ricerca nella home</a>: cerca tra i titoli e le '
              f'parole delle note di tutti i {NUM["n_tot"]} codici ATECO 2025 e tra i vecchi codici ATECO 2022. Istat avverte che gli esempi delle note '
              f'di inclusione non sono un elenco completo: conta l\'attività svolta davvero.{rim.ref("istat_ateco")}</p></div>')
    corpo += nota(f"Queste guide riportano i codici della classificazione ufficiale, non una consulenza: {FRASE_FISSA}.", "info", "alert")
    corpo += rim.elenco()
    testata = banda("Codice ATECO per attività", "Codice ATECO per attività",
                    f"{len(voci)} guide alle attività più cercate, dal bar all'avvocato, dal B&B all'elettricista.", corta=True, icona="tag")
    pagina("codice-ateco-per/", f"Codice ATECO per attività: {len(voci)} guide con le note Istat",
           f"Il codice ATECO 2025 per {len(voci)} attività cercate: bar, avvocato, B&B, estetista, edilizia e altre, con le note Istat, i vecchi codici e il forfettario.",
           corpo, testata, briciole=[("Home", ""), ("Per attività", "codice-ateco-per/")])


def misura_attivita():
    """Pagine attività: indicizzate solo con almeno MIN_PAROLE_PROPRIE gruppi di 5 parole che non sono in nessun'altra pagina (di codice o di
    attività) e meno di MAX_SOVRAPPOSIZIONE_ATTIVITA di testo in comune con la pagina più simile. Le righe Istat citate spezzano il testo e
    contano solo come testo in comune; le frasi di modello (≥ 25% delle pagine attività) non contano."""
    global _PROVA
    _PROVA = {}
    pagine_codice()
    cod = {p: gruppi_di_parole(t) for p, t in _PROVA.items()}
    _PROVA = {}
    for a in ATTIVITA:
        pagina_attivita(a)
    testi, _PROVA = _PROVA, None
    att = {p: gruppi_di_parole(t, citazioni_a_parte=True) for p, t in testi.items()}
    conta_cod = Counter(g for s in cod.values() for g in s)
    conta_att = Counter(g for s in att.values() for g in s)
    modello = {g for g, n in conta_att.items() if n >= QUOTA_MODELLO_ATTIVITA * len(att)}
    att = {p: s - modello for p, s in att.items()}
    indice = defaultdict(set)
    for q, s in list(cod.items()) + list(att.items()):
        for g in s:
            if conta_cod[g] + conta_att[g] <= 60:
                indice[g].add(q)
    tutti = {**cod, **att}
    for p, a in att.items():
        proprie = sum(1 for g in a if conta_cod[g] == 0 and conta_att[g] == 1)
        cand = Counter(q for g in a for q in indice[g] if q != p)
        meglio = (0.0, "")
        for q, _ in cand.most_common(15):
            x = len(a & tutti[q]) / len(a) if a else 0
            if x > meglio[0]:
                meglio = (round(x, 3), q)
        MISURA_ATT[p] = {"proprie": proprie, "sovrapposizione": meglio[0], "piu_simile": meglio[1]}
        INDICIZZA_ATT[p] = proprie >= MIN_PAROLE_PROPRIE and meglio[0] < MAX_SOVRAPPOSIZIONE_ATTIVITA


# ---------------------------------------------------------------- pagine del sito
MODULO = """<form name="segnalazioni" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card">
<input type="hidden" name="form-name" value="segnalazioni">
<p class="hp"><label>Lascia vuoto questo campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Pagina o codice<input type="text" name="pagina" required maxlength="300" placeholder="Per esempio /56-11/ o 56.11.11"></label>
<label>Cosa non torna con le tabelle Istat?<textarea name="messaggio" required rows="5" maxlength="3000"></textarea></label>
<label>Fonte ufficiale (facoltativa)<input type="url" name="fonte" maxlength="500" placeholder="https://"></label>
<label>La tua email (facoltativa, solo se vuoi una risposta)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>Accetto che il messaggio, e l'email se l'ho scritta, siano conservati per controllare e rispondere alla segnalazione (vedi la <a href="/privacy/#segnalazioni">privacy</a>).</span></label>
<button type="submit" class="btn">Invia la segnalazione</button>
</form>"""


def come_lavoriamo(n_idx, n_noidx):
    rim = Rimandi()
    corpo = ('<div class="card pull"><p style="margin:0"><strong>Usiamo solo i file ufficiali dell\'Istat e i testi di legge, con la loro data.</strong> '
             f'Non riscriviamo titoli e note: li riportiamo come li pubblica l\'Istat. Non diciamo quale codice scegliere: per questo, {FRASE_FISSA}.</p></div>')
    corpo += '<h2 id="fonti-usate">I file che usiamo</h2>'
    rr = []
    for fid, f in FJ["file"].items():
        rr.append([f'<a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a>{rim.ref(fid)}', data_lunga(f["letto_il"]), num(f["byte"]), f'<code>{f["sha256"][:12]}</code>'])
    for pid, p in FJ["pagine"].items():
        rr.append([f'<a href="{h(p["url"])}" rel="noopener">{h(p["titolo"])}</a>{rim.ref(pid)}', data_lunga(p["letto_il"]), num(p["byte"]), f'<code>{p["sha256"][:12]}</code>'])
    corpo += tabella(["File o pagina", "Letto il", "Byte", "Impronta"], rr, num_=[2],
                     caption="L'impronta (SHA-256, prime 12 cifre) identifica il file letto: se cambia, rifacciamo tutti i controlli.")
    corpo += (f'<h2 id="licenza">Licenza e attribuzione</h2><p>{ATTRIBUZIONE} La licenza permette il riuso anche commerciale con l\'obbligo di citare la fonte, '
              f'fornire un link alla licenza e indicare le modifiche.{rim.ref("istat_note_legali")} Questo sito non è approvato né sostenuto dall\'Istat.</p>')
    corpo += '<h2 id="metodo">Cosa facciamo con i dati</h2><div class="testo"><ol>'
    corpo += (f'<li><strong>Albero.</strong> {NUM["n_tot"]} codici dal file della struttura: ogni codice ha il suo padre, e il controllo automatico verifica che '
              'nessun codice manchi o sia doppio.</li>'
              '<li><strong>Note.</strong> Le note esplicative Istat (centrali, di inclusione, di inclusione aggiuntiva, di esclusione e operative) sono riportate '
              'parola per parola; i codici citati dopo «cfr.» diventano link.</li>'
              '<li><strong>Vecchi codici.</strong> Le corrispondenze vengono dalla tavola di raccordo bidirezionale (aggiornamento 2026), con il «contenuto in comune» '
              'scritto da Istat; il codice rappresentativo dalla tabella operativa di riclassificazione.</li>'
              '<li><strong>Forfettario.</strong> Per ogni sottocategoria ATECO 2025 prendiamo i codici ATECO 2022 collegati nella tavola di raccordo e li '
              'confrontiamo con i codici ATECO 2007 della tabella di legge. ATECO 2022 è l\'aggiornamento 2022 di ATECO 2007 e non cambia divisioni, gruppi e classi. '
              'È un abbinamento nostro, fatto con fonti ufficiali: la legge chiede il codice ATECO 2007 della singola attività.</li></ol></div>')
    corpo += ('<h2 id="pagine">Quali pagine pubblichiamo</h2><div class="testo">'
              f'<p>Una pagina per ogni sezione ({NUM["n_1"]}), divisione ({NUM["n_2"]}) e classe ({NUM["n_4"]}). Le {NUM["n_6"]} sottocategorie a sei cifre sono '
              'schede dentro la pagina della loro classe, con un indirizzo proprio (#c- e il codice): molte hanno lo stesso titolo della classe e poche righe di '
              f'note, e pagine separate sarebbero quasi uguali. Chiediamo ai motori di ricerca di indicizzare {n_idx} pagine di codice, quelle con almeno '
              f'{MIN_PAROLE_PROPRIE} gruppi di parole propri e meno del {int(MAX_SOVRAPPOSIZIONE * 100)}% di testo in comune con la pagina più simile; le altre '
              f'{n_noidx} restano consultabili ma non indicizzate e senza pubblicità. Le pagine «codice ATECO per mestiere» e «codice ATECO per '
              f'attività» esistono solo per le attività con ricerche misurate su Google (almeno {MIN_VOLUME_ATTIVITA} al mese per le guide per attività): '
              'citano parola per parola le note Istat e i titoli ufficiali e vengono indicizzate solo se hanno abbastanza testo proprio, con meno del '
              f'{int(MAX_SOVRAPPOSIZIONE_ATTIVITA * 100)}% in comune con la pagina più simile.</p></div>')
    corpo += ('<h2 id="aggiornamenti">Ogni quanto aggiorniamo</h2><div class="testo"><p>Ogni mese ricarichiamo i file Istat e le pagine di legge: se un\'impronta '
              'cambia rifacciamo tutti i controlli. Istat ha annunciato aggiornamenti più frequenti della classificazione dal 2026.</p></div>')
    corpo += ('<h2 id="segnala">Segnala un errore</h2><p>Hai trovato una differenza con le tabelle Istat? Scrivici la pagina e, se puoi, il link alla fonte. '
              'L\'email è facoltativa.</p>' + MODULO)
    corpo += rim.elenco()
    testata = banda("Come lavoriamo", "Come leggiamo e controlliamo i file Istat",
                    "Quali file usiamo, con che data, cosa abbiniamo, quali pagine indicizziamo e ogni quanto aggiorniamo.", corta=True, icona="shield")
    pagina("come-lavoriamo/", "Come lavoriamo: file Istat, controlli e aggiornamenti",
           "Come Codici ATECO 2025 usa la struttura, le note, la tavola di raccordo e la tabella operativa Istat: impronte dei file, controlli e licenza.",
           corpo, testata, briciole=[("Home", ""), ("Come lavoriamo", "come-lavoriamo/")])


def chi_siamo():
    corpo = ('<div class="card pull testo"><p><strong>Codici ATECO 2025 è un sito informativo indipendente e gratuito.</strong> Mette in pagine semplici la '
             'classificazione delle attività economiche dell\'Istat, con le note ufficiali, i vecchi codici e i coefficienti del forfettario.</p></div>'
             '<h2>Perché esiste</h2><div class="testo"><p>I file ufficiali sono fogli di calcolo con migliaia di righe: struttura, note e corrispondenze stanno in '
             'file diversi. Qui li trovi già uniti, codice per codice, con la fonte accanto.</p></div>'
             '<h2>Cosa non siamo</h2><div class="testo"><ul><li>Non siamo l\'Istat, l\'Agenzia delle entrate o una Camera di commercio, e non siamo affiliati a '
             'nessuno di loro.</li><li>Non diamo consulenza fiscale: per la scelta del codice e del regime, verifica con il commercialista o la Camera di '
             'commercio.</li><li>Non raccogliamo dati di chi legge, a parte il modulo facoltativo per segnalare un errore.</li></ul></div>'
             '<h2>Come si sostiene</h2><div class="testo"><p>Il sito può mostrare pubblicità di Google AdSense nelle pagine con più contenuto. La pubblicità non '
             'cambia nessun dato e nessuno paga per comparire.</p><p>Codici ATECO 2025 fa parte di una piccola rete di siti informativi gratuiti dello stesso '
             'gestore. Come controlliamo i dati: <a href="/come-lavoriamo/">come lavoriamo</a>.</p></div>')
    testata = banda("Chi siamo", "Chi siamo", "Un sito indipendente che rende leggibile la classificazione ATECO 2025.", corta=True, icona="people")
    pagina("chi-siamo/", "Chi siamo | Codici ATECO 2025",
           "Codici ATECO 2025 è un sito indipendente e gratuito, non affiliato a Istat, con codici, note ufficiali, vecchi codici e coefficienti del forfettario.",
           corpo, testata, briciole=[("Home", ""), ("Chi siamo", "chi-siamo/")])


def privacy():
    aff = any(v.get("url") for k, v in AFF.items() if not k.startswith("_"))
    cookie = MON.privacy_cookie("it", SITO_ID, aff) or ('<h2>Cookie e contatore visite</h2><p>Per contare le visite usiamo GoatCounter, che non usa cookie. '
                                                       'Il sito non usa cookie di profilazione e non mostra pubblicità.</p>')
    corpo = ('<div class="card pull testo"><p>Questa pagina spiega quali dati tratta Codici ATECO 2025. In breve: pochissimi.</p></div>'
             '<div class="testo"><h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce Codici ATECO 2025 come progetto '
             'indipendente. Puoi scriverci con il modulo <a href="/come-lavoriamo/#segnala">«Segnala un errore»</a>, anche per le richieste sui tuoi dati.</p>'
             '<h2>La ricerca dei codici</h2><p>La ricerca nella home e il filtro della tabella di conversione funzionano nel tuo browser: le parole che scrivi non '
             'vengono inviate né salvate. Il sito ricorda nel browser solo la scelta del tema chiaro o scuro (memoria locale).</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>Il sito è ospitato da Netlify, Inc., che tratta dati tecnici (come l\'indirizzo IP) per consegnare le pagine e proteggere il servizio. '
             'Netlify può trattare i dati fuori dall\'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>'
             '<h2 id="segnalazioni">Modulo «Segnala un errore»</h2><p>Se usi il modulo riceviamo la pagina che indichi, il messaggio, il link alla fonte e, solo se la '
             'scrivi, la tua email. Il modulo è gestito da Netlify Forms per nostro conto. Usiamo questi dati solo per controllare la segnalazione e, se hai lasciato '
             'l\'email, risponderti; li cancelliamo quando la segnalazione è chiusa. La base giuridica è il consenso dato con la casella del modulo (art. 6.1.a GDPR), '
             'che puoi ritirare quando vuoi: per chiedere la cancellazione basta un\'altra segnalazione. Non ci sono account né newsletter.</p>'
             '<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e fare reclamo al '
             'Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>'
             f'<h2>Modifiche</h2><p>Aggiorniamo questa pagina quando il sito cambia. Ultimo aggiornamento: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("it", SITO_ID, aff) or "Cosa raccogliamo (pochissimo) e come funziona il contatore delle visite."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", "Privacy | Codici ATECO 2025",
           "Privacy di Codici ATECO 2025: ricerca nel browser, contatore delle visite senza cookie e pubblicità solo con il tuo consenso.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = ('<div class="card pull"><p>La pagina che cerchi non esiste. Torna alla <a href="/#cerca">ricerca dei codici</a>, all\'<a href="/#sezioni">elenco delle '
             'sezioni</a> o alla <a href="/da-ateco-2022-a-2025/">tabella da ATECO 2022 a 2025</a>.</p></div>')
    testata = banda("Errore 404", "Pagina non trovata", "Questo indirizzo non ha una pagina.", corta=True, icona="alert")
    pagina("", "Pagina non trovata | Codici ATECO 2025", "Pagina non trovata.", corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{CONTROLLO.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in ateco/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = ateco/sito, Build command vuoto, Publish directory = "."
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


# ---------------------------------------------------------------- indicizzazione delle pagine di codice
def gruppi_di_parole(html_, n=5, citazioni_a_parte=False):
    """citazioni_a_parte (pagine attività): ogni riga Istat citata (<q class="ni">) è tolta e spezza il testo, così gli accostamenti di righe
    ufficiali diverse non contano come testo proprio. I blocchi <section data-ripreso> (link alle guide) non contano mai."""
    t = re.sub(r"<section data-ripreso>.*?</section>", " ", html_, flags=re.S)
    t = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", t, flags=re.S | re.I)
    if citazioni_a_parte:
        t = re.sub(r'<q class="ni"[^>]*>.*?</q>', " \x00 ", t, flags=re.S)
    out = set()
    for pezzo in unescape(re.sub(r"<[^>]+>", " ", t)).lower().split("\x00"):
        w = re.findall(r"\w+", pezzo)
        out |= {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}
    return out


def pagine_codice():
    for s in SEZIONI:
        pagina_sezione(s)
    for d in DIVISIONI:
        pagina_divisione(d)
    for c in CLASSI:
        pagina_classe(c)


MISURA = {}  # percorso -> {"proprie", "sovrapposizione", "piu_simile"}


def misura():
    """Testo proprio e sovrapposizione di ogni pagina di codice con la più simile (gruppi di 5 parole)."""
    global _PROVA
    _PROVA = {}
    pagine_codice()
    testi, _PROVA = _PROVA, None
    ins = {p: gruppi_di_parole(t) for p, t in testi.items()}
    conta = Counter(g for s in ins.values() for g in s)
    indice = defaultdict(list)  # gruppo raro -> pagine (per trovare in fretta le candidate più simili)
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
    misura_attivita()
    home()
    pagine_codice()
    da_2022()
    cosa_cambia()
    coefficienti()
    for m in MESTIERI_PUBBLICATI:
        pagina_mestiere(m)
    for a in ATTIVITA:
        pagina_attivita(a)
    indice_attivita()
    n_idx = sum(INDICIZZA.values())
    come_lavoriamo(n_idx, len(INDICIZZA) - n_idx)
    chi_siamo()
    privacy()
    pagina_404()
    extra()
    (DATI / "indicizzazione.json").write_text(json.dumps({
        "_nota": "Scritto da genera.py: perché ogni pagina di codice è indicizzata o no (verifica.py ricalcola le misure dalle pagine).",
        "regola": {"min_parole_proprie": MIN_PAROLE_PROPRIE, "max_sovrapposizione": MAX_SOVRAPPOSIZIONE},
        "pagine": {p: dict(MISURA[p], indicizzata=INDICIZZA[p]) for p in sorted(MISURA)},
        "mestieri": {m["slug"]: {"volume": volume_mestiere(m), "pubblicata": volume_mestiere(m) > 0} for m in MES},
        "regola_attivita": {"min_volume_mensile": MIN_VOLUME_ATTIVITA, "min_parole_proprie": MIN_PAROLE_PROPRIE,
                            "max_sovrapposizione": MAX_SOVRAPPOSIZIONE_ATTIVITA, "quota_modello_attivita": QUOTA_MODELLO_ATTIVITA},
        "attivita": {a["slug"]: {"volume": volume_attivita(a), "pubblicata": a in ATTIVITA,
                                 **({**MISURA_ATT[a["slug"] + "/"], "indicizzata": INDICIZZA_ATT[a["slug"] + "/"]} if a in ATTIVITA else {})} for a in ATT}},
        ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili ({n_idx} pagine di codice su {len(INDICIZZA)}, "
          f"{len(INDICIZZA) - n_idx} noindex) + 404. Mestieri pubblicati: {', '.join(m['slug'] for m in MESTIERI_PUBBLICATI)}. "
          f"Pagine attività: {len(ATTIVITA)} ({sum(INDICIZZA_ATT.values())} indicizzate).")


if __name__ == "__main__":
    main()
