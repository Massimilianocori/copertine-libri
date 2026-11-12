"""Genera il sito statico "Farmaco Equivalente" (italiano) in farmaci/sito/: equivalenti, differenza da pagare e carenze
dalle liste ufficiali AIFA, confezione per confezione.

Uso (dalla radice del repository):
    python3 -I farmaci/raccolta/fonti.py      # scarica i file AIFA -> raccolta/_grezzi/, dati/fonti.json
    python3 -I farmaci/raccolta/estrai.py     # legge i file -> dati/trasparenza.json, dati/carenti.json, dati/classe_a.json
    python3 -I farmaci/raccolta/domanda.py    # ricerche vere (autocompletamento) -> dati/domanda.json
    python3 farmaci/genera.py                 # pagine in farmaci/sito/
    python3 farmaci/verifica.py --browser     # controlli (ricalcola tutto dai file grezzi)

Regole: solo dati AIFA con la data della lista accanto; nessun consiglio medico; frase fissa «chiedi al medico o al
farmacista»; nessuna pubblicità né link di affiliazione a farmaci con ricetta. Una pagina per principio attivo con un
blocco per ogni gruppo di equivalenza; si indicizza solo se c'è una ricerca vera (equivalente, generico, prezzo,
carenza...) per il principio attivo o per uno dei suoi nomi commerciali. Le altre pagine restano noindex e senza pubblicità.
"""
import functools
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from html import escape, unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import nomi  # noqa: E402
import stile  # noqa: E402

URL_SITO = "https://farmaci-equivalenti.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
NOME = "Farmaco Equivalente"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "farmaci"  # nome del sito in monetizzazione.json
MIN_PAROLE_ADSENSE = 400  # niente pubblicità nelle pagine noindex o con poco testo (lezione AdSense «scarso valore»)
FRASE_FISSA = "chiedi al medico o al farmacista"

# Ricerche che contano come domanda per una pagina (stessa espressione di raccolta/domanda.py)
INTERESSE = re.compile(r"generic|equivalent|alternativ|sostitut|prezz|cost[oa]|mutuabil|non si trova|carenz|carent|mancant|introvabil|"
                       r"esaurit|ritirat|differenza|simile|uguale|al posto", re.I)
TIPO_EQ = re.compile(r"generic|equivalent|alternativ|sostitut|simile|uguale|al posto", re.I)
TIPO_PREZZO = re.compile(r"prezz|cost[oa]|differenza", re.I)
TIPO_CAR = re.compile(r"non si trova|carenz|carent|mancant|introvabil|esaurit|ritirat", re.I)

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
TR = carica("trasparenza.json")
CA = carica("carenti.json")
DOM = carica("domanda.json")
FAQ = carica("faq.json")["faq"]
DATA_T = date.fromisoformat(TR["pubblicato_il"])
DATA_C = date.fromisoformat(CA["pubblicato_il"])
CONTROLLO = max(date.fromisoformat(x["letto_il"]) for x in FJ["file"].values())


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    g = "1°" if d.day == 1 else str(d.day)
    return f"{g} {MESI[d.month - 1]} {d.year}"


def data_breve(d):
    if not d:
        return ""
    d = date.fromisoformat(d) if isinstance(d, str) else d
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def euro(x):
    x = Decimal(str(x)).quantize(Decimal("0.01"))
    s = f"{abs(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if x < 0 else "") + s + " €"


def num(n):
    return f"{n:,}".replace(",", ".")


def D(x):
    return Decimal(str(x))


# ---------------------------------------------------------------- dati
RIGHE = TR["righe"]
# Lo stesso principio attivo a volte è scritto con maiuscole diverse (es. «Losartan + Idroclorotiazide» e «... + idroclorotiazide»):
# una sola pagina, con la grafia più frequente nella lista.
_VAR = defaultdict(Counter)
for r in RIGHE:
    _VAR[nomi.slug(r["pa"])][r["pa"]] += 1
for r in RIGHE:
    r["pa_aifa"] = r["pa"]
    r["pa"] = sorted(_VAR[nomi.slug(r["pa"])].items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
GRUPPI = defaultdict(list)
for r in RIGHE:
    GRUPPI[r["gruppo"]].append(r)
PA = defaultdict(list)
for r in RIGHE:
    PA[r["pa"]].append(r)
CAR = defaultdict(list)
for c in CA["righe"]:
    CAR[c["aic"]].append(c)
AIC_T = {r["aic"]: r for r in RIGHE}
SLUG = {p: nomi.slug(p) for p in PA}
if len(set(SLUG.values())) != len(SLUG):
    raise SystemExit("due principi attivi con lo stesso indirizzo")
RISERVATI = {"carenze", "farmaco-mancante", "come-lavoriamo", "chi-siamo", "privacy", "assets"}
if RISERVATI & set(SLUG.values()):
    raise SystemExit(f"indirizzo riservato usato da un principio attivo: {RISERVATI & set(SLUG.values())}")


def gruppi_pa(pa):
    codici = []
    for r in PA[pa]:
        if r["gruppo"] not in codici:
            codici.append(r["gruppo"])
    return codici


def righe_gruppo(g):
    return sorted(GRUPPI[g], key=lambda r: (D(r["diff"]), r["farmaco"], r["aic"]))


def carente(aic):
    return aic in CAR


def stato_carenza(c):
    """Etichetta della carenza: «carente dal» oppure «carenza prevista dal» (data di inizio dopo la data dell'elenco)."""
    if c["inizio"] and c["inizio"] > CA["pubblicato_il"]:
        return f"Carenza prevista dal {data_breve(c['inizio'])}"
    return f"Carente dal {data_breve(c['inizio'])}" if c["inizio"] else "Carente"


def conf_txt(s):
    """Confezione di riferimento AIFA in forma leggibile (il testo ufficiale resta accanto, invariato)."""
    t = s.lower().replace("unita'", "unità").replace(" - ", ", ")
    t = re.sub(r"\bui\b", "UI", t)
    t = re.sub(r"\s+", " ", t).strip(" ,")
    return t[0].upper() + t[1:]


def pa_txt(p):
    return p.replace(" + ", " + ")


def atc_pa(pa):
    return sorted({r["atc"] for r in PA[pa]})


def carenti_extra(pa):
    """Righe dell'elenco carenti con lo stesso codice ATC del principio attivo ma fuori dalla lista di trasparenza."""
    atc = set(atc_pa(pa))
    return sorted([c for c in CA["righe"] if c["atc"] in atc and c["aic"] not in AIC_T], key=lambda c: (c["nome"], c["aic"]))


# ---------------------------------------------------------------- domanda (ricerche vere)
def chiavi_pa(pa):
    ch = [nomi.pa_ricerca(pa)]
    for r in PA[pa]:
        if nomi.di_fantasia(r["farmaco"], r["pa"]):
            m = nomi.marchio(r["farmaco"])
            if m not in ch:
                ch.append(m)
    return ch


SUGG_RADICI = [s for v in DOM["radici"].values() for s in v]


def prove_domanda(pa):
    """{chiave: [suggerimenti]} con le ricerche vere che citano la chiave e una parola d'interesse."""
    out = {}
    for k in chiavi_pa(pa):
        rx = re.compile(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])")
        sugg = list(DOM["nomi"].get(k, [])) + SUGG_RADICI
        ok = []
        for s in sugg:
            if rx.search(s) and INTERESSE.search(s.replace(k, " ")) and s not in ok:
                ok.append(s)
        if ok:
            out[k] = ok
    return out


PROVE = {pa: prove_domanda(pa) for pa in PA}
LETTI = {pa: all(k in DOM["nomi"] for k in chiavi_pa(pa)) for pa in PA}
# Interruttore per il revisore: con False si indicizzano solo le pagine con ricerche su equivalente/generico/carenza
# (oggi 90 principi attivi invece di 334); le altre restano consultabili, noindex e senza pubblicità.
INDICIZZA_CON_SOLO_PREZZO = True


def _indicizza(pa):
    s = [x for v in PROVE[pa].values() for x in v]
    if not s:
        return False
    return INDICIZZA_CON_SOLO_PREZZO or any(TIPO_EQ.search(x) or TIPO_CAR.search(x) for x in s)


INDICIZZA = {pa: _indicizza(pa) for pa in PA}


@functools.lru_cache(maxsize=None)
def marchio_principale(pa):
    """Nome commerciale da mettere nel titolo: quello con più ricerche d'interesse (se ce n'è uno)."""
    cand = []
    for k, v in PROVE[pa].items():
        if k == nomi.pa_ricerca(pa):
            continue
        nelle_radici = sum(1 for x in v if x in SUGG_RADICI)
        diff_max = max(D(r["diff"]) for r in righe_marchio(pa, k)) if righe_marchio(pa, k) else Decimal(0)
        cand.append((nelle_radici, len(v), diff_max, k))
    if not cand:
        return None
    # prima i nomi citati nelle ricerche generali («equivalente di augmentin»), poi più ricerche d'interesse, poi la differenza più alta
    cand.sort(key=lambda x: (-x[0], -x[1], -x[2], x[3]))
    return cand[0][3]


def righe_marchio(pa, m):
    return [r for r in PA[pa] if nomi.di_fantasia(r["farmaco"], r["pa"]) and nomi.marchio(r["farmaco"]) == m]


def bello(m):
    return m[:1].upper() + m[1:]


# ---------------------------------------------------------------- fonti numerate
FONTI_DEF = {}
for fid, f in FJ["file"].items():
    FONTI_DEF[fid] = {"titolo": f["titolo"], "chi": f["chi"], "url": f["pagina"], "data": f["pubblicato_il"], "letto": f["letto_il"],
                      "file": f["url"]}
for pid, p in FJ["pagine"].items():
    FONTI_DEF[pid] = {"titolo": p["titolo"], "chi": p["chi"], "url": p["url"], "data": None, "letto": p["letto_il"], "file": None}


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
            pub = f' Pubblicato da AIFA il {data_lunga(f["data"])}.' if f["data"] else ""
            file_ = f' <a href="{h(f["file"])}" rel="noopener">File</a>.' if f["file"] else ""
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}.{pub}{file_} '
                        f'<span class="small">Letto il {data_lunga(f["letto"])}.</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Fonti</h2><ol>{"".join(voci)}</ol>'
                f'<p class="small">Dati AIFA riutilizzati con licenza <a href="{FJ["licenza"]["url"]}" rel="noopener">CC BY 4.0</a>; '
                f'la presentazione e i conteggi sono nostri. Come lavoriamo: <a href="/come-lavoriamo/">metodo e controlli</a>.</p></section>')


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
AD = '<div class="ad-slot" aria-hidden="true"></div>'
MENU = [("carenze/", "Farmaci carenti"), ("farmaco-mancante/", "Farmaco che manca"), ("#indice", "Principi attivi"), ("come-lavoriamo/", "Come lavoriamo")]
DISCLAIMER = (f"<strong>Informazioni dagli elenchi ufficiali AIFA, non consigli medici.</strong> Questo sito non fa diagnosi e non dice quale farmaco "
              f"prendere: non cambiare né sospendere una terapia di tua iniziativa, {FRASE_FISSA}. "
              f"Sito indipendente, non affiliato ad AIFA. Prezzi al pubblico da lista AIFA del {data_lunga(DATA_T)}; in farmacia possono variare "
              f"per i farmaci di fascia C. Elenco dei farmaci carenti AIFA del {data_lunga(DATA_C)}.")


def parole_principali(corpo):
    t = re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    return len(re.findall(r"\w+", t))


def menu_html(percorso):
    out = ""
    for u, t in MENU:
        href = "/" + u if not u.startswith("#") else "/" + u
        cur = ' aria-current="page"' if (percorso and not u.startswith("#") and percorso.startswith(u)) else ""
        out += f'<a href="{href}"{cur}>{h(t)}</a>'
    return out


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
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
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{adsense}
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
<meta name="theme-color" content="#0E2F2C">
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
<a class="logo" href="/">{LOGO}<span>Farmaco <b>Equivalente</b></span></a>
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
<a class="logo" href="/">{LOGO}<span>Farmaco <b>Equivalente</b></span></a>
<p><strong>{NOME}</strong> mette in pagine leggibili la lista di trasparenza e l'elenco dei farmaci carenti pubblicati da AIFA, con la data di ogni
elenco. È un sito indipendente, non affiliato ad AIFA, al Ministero della Salute, a farmacie o ad aziende farmaceutiche.</p>
<p>Dati: Agenzia Italiana del Farmaco, licenza <a href="{FJ["licenza"]["url"]}" rel="noopener">CC BY 4.0</a>. Lista di trasparenza del {data_lunga(DATA_T)},
elenco dei carenti del {data_lunga(DATA_C)}.</p>
</div><div>
<h2>Elenchi</h2><ul><li><a href="/">Cerca un farmaco</a></li><li><a href="/carenze/">Farmaci carenti</a></li>
<li><a href="/farmaco-mancante/">Farmaco che non si trova</a></li><li><a href="/#indice">Tutti i principi attivi</a></li></ul>
</div><div>
<h2>Il sito</h2><ul><li><a href="/come-lavoriamo/">Come lavoriamo</a></li><li><a href="/come-lavoriamo/#segnala">Segnala un errore</a></li>
<li><a href="/chi-siamo/">Chi siamo</a></li><li><a href="/privacy/">Privacy</a></li></ul>
</div></div>
<p class="f-base">Informazioni generali dagli elenchi ufficiali, non consigli medici: {FRASE_FISSA}. Gli elenchi originali sono sul sito
dell'<a href="https://www.aifa.gov.it/open-data" rel="noopener">Agenzia Italiana del Farmaco</a>.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="pill"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def tabella(intest, righe, caption="", num=None, classi=None, attr=None, id_=None, resp="", etichette=None):
    """resp: classe per il telefono ("resp" = righe come schede, con l'intestazione di ogni colonna accanto al valore)."""
    num = num if num is not None else []
    th = "".join(f'<th scope="col"{" class=\"n\"" if i in num else ""}>{x}</th>' for i, x in enumerate(intest))
    etich = etichette or [re.sub(r"<[^>]+>", "", x) for x in intest]
    body = ""
    for k, r in enumerate(righe):
        cl = f' class="{classi[k]}"' if classi and classi[k] else ""
        at = attr[k] if attr else ""
        body += f"<tr{cl}{at}>" + "".join(f'<td{" class=\"n\"" if i in num else ""}{f" data-l=\"{h(etich[i])}\"" if resp and i else ""}>{x}</td>'
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
    return (f'<h2 id="faq">{h(titolo)}</h2><p class="small">Domande che le persone cercano davvero su Google, con la risposta presa '
            f'dagli elenchi AIFA e dalla legge.</p>' + blocchi), ld


# ---------------------------------------------------------------- numeri generali (usati da home, FAQ e come lavoriamo)
CAR_SET = set(CAR)
CAR_IN_T = [c for c in CA["righe"] if c["aic"] in AIC_T]
CAR_IN_T_AIC = sorted({c["aic"] for c in CAR_IN_T})
CON_EQ_NON_CAR = [a for a in CAR_IN_T_AIC if any(x["aic"] not in CAR_SET for x in GRUPPI[AIC_T[a]["gruppo"]])]
NUM = {
    "data_t": data_lunga(DATA_T), "data_c": data_lunga(DATA_C),
    "n_conf": num(len(RIGHE)), "n_gruppi": num(len(GRUPPI)), "n_pa": num(len(PA)),
    "n_diff": num(sum(1 for r in RIGHE if D(r["diff"]) > 0)),
    "n_car": num(len(CA["righe"])), "n_car_aic": num(len(CAR)), "n_car_pa": num(len({c["pa"] for c in CA["righe"]})),
    "n_car_eq": num(sum(1 for c in CA["righe"] if c["equivalente"].lower().startswith("s"))),
    "n_cessata": num(sum(1 for c in CA["righe"] if c["motivo"] == "Cessata commercializzazione definitiva")),
    "n_car_t": num(len(CAR_IN_T_AIC)), "n_car_t_eq": num(len(CON_EQ_NON_CAR)),
}


def faq_fisse(pid, rim):
    voci = []
    for x in FAQ:
        if x["pagina"] == pid:
            voci.append((x["q"], x["a"].format(**NUM), rim.ref(x["fonti"])))
    return voci


# ---------------------------------------------------------------- pagina del principio attivo
def riga_tabella(r):
    cs = CAR.get(r["aic"])
    tag = (f'<span class="tag car">{h(stato_carenza(cs[0]))}</span>' if cs else '<span class="tag neu">Non in elenco</span>')
    diff = D(r["diff"])
    d_txt = "nessuna" if diff == 0 else euro(diff)
    nome = f'<strong>{h(r["farmaco"])}</strong><small>{h(r["confezione"])}</small><small>{h(r["ditta"])} · AIC {r["aic"]}</small>'
    if r["nota"]:
        nome += f'<small>Nota AIFA: {h(r["nota"])}</small>'
    attr = (f' data-aic="{r["aic"]}" data-prezzo="{r["prezzo"]}" data-rif="{r["rif"]}" data-diff="{r["diff"]}" data-carente="{1 if cs else 0}"'
            f' id="aic-{r["aic"]}"')
    return [nome, euro(r["prezzo"]), d_txt, tag], ("carente" if cs else ""), attr


def blocco_carenza(c, rim):
    fine = data_lunga(c["fine_presunta"]) if c["fine_presunta"] else "non indicata da AIFA"
    el = {"equivalenti": "farmaci carenti con equivalenti disponibili", "alternativo": "farmaci carenti con trattamento alternativo"}
    elenchi = "; ".join(el[e] for e in c["elenchi"])
    righe = [f'<p><strong>{h(c["nome"])}</strong> (AIC {c["aic"]}): {h(stato_carenza(c).lower())}, fine presunta {fine}. '
             f'Motivo indicato da AIFA: {h(c["motivo"] or "non indicato")}.{rim.ref("carenti")}</p>']
    if c["suggerimenti"]:
        righe.append(f'<p>Indicazione AIFA: «{h(c["suggerimenti"])}»</p>')
    if c["nota"]:
        righe.append(f'<p>Nota AIFA: «{h(c["nota"])}»</p>')
    if elenchi:
        righe.append(f'<p class="small">Compare anche nell\'elenco AIFA dei {elenchi}.</p>')
    return '<div class="det">' + "".join(righe) + "</div>"


def sezione_gruppo(g, rim):
    rr = righe_gruppo(g)
    r0 = rr[0]
    rif = D(r0["rif"])
    zero = [r for r in rr if D(r["diff"]) == 0]
    massimo = max(rr, key=lambda r: (D(r["diff"]), r["farmaco"]))
    car = [r for r in rr if carente(r["aic"])]
    non_car = [r for r in rr if not carente(r["aic"])]
    gid = "g-" + g.lower()
    out = f'<section class="gruppo" id="{gid}" aria-labelledby="{gid}-h"><h2 id="{gid}-h">{h(conf_txt(r0["conf_rif"]))}</h2>'
    out += (f'<p class="gruppo-h"><span>Gruppo di equivalenza AIFA {h(g)}</span><span>ATC {h(r0["atc"])}</span>'
            f'<span>Confezione di riferimento: {h(r0["conf_rif"])}</span></p>')
    frase = (f'<p>Prezzo di riferimento rimborsato dal Servizio sanitario: <strong>{euro(rif)}</strong>.{rim.ref("trasparenza")} '
             f'{len(rr)} confezion{"e" if len(rr) == 1 else "i"} nel gruppo')
    if len(rr) > 1:
        frase += (f': {len(zero)} senza differenza da pagare' + (
            f', la differenza più alta è {euro(massimo["diff"])} ({h(massimo["farmaco"])})' if D(massimo["diff"]) > 0 else "") + ".")
    else:
        frase += (": nella lista c'è solo questa." if D(r0["diff"]) == 0 else f": differenza {euro(r0['diff'])}.")
    out += frase + "</p>"
    if car:
        nc_zero = [r for r in non_car if D(r["diff"]) == 0]
        if non_car:
            nomi_nc = sorted({r["farmaco"] for r in (nc_zero or non_car)})
            el = ", ".join(h(n) for n in nomi_nc[:8]) + (f" e altri {len(nomi_nc) - 8}" if len(nomi_nc) > 8 else "")
            out += nota(f'<strong>{len(car)} confezion{"e" if len(car) == 1 else "i"} di questo gruppo {"è" if len(car) == 1 else "sono"} nell\'elenco AIFA dei '
                        f'farmaci carenti del {data_lunga(DATA_C)}.</strong> Equivalenti non carenti nello stesso gruppo: {len(non_car)}'
                        + (f', di cui {len(nc_zero)} senza differenza da pagare: {el}.' if nc_zero else f': {el}.')
                        + f' La sostituzione la decide il medico o la propone il farmacista: {FRASE_FISSA}.', "", "alert")
        else:
            out += nota(f'<strong>Tutte le confezioni di questo gruppo sono nell\'elenco AIFA dei farmaci carenti del {data_lunga(DATA_C)}.</strong> '
                        f'Nella lista di trasparenza non c\'è un equivalente non carente: {FRASE_FISSA}.', "", "alert")
    righe, classi, attr = [], [], []
    for r in rr:
        a, b, c = riga_tabella(r)
        righe.append(a)
        classi.append(b)
        attr.append(c)
    out += tabella(["Farmaco e confezione", "Prezzo al pubblico", "Differenza a carico", "Elenco carenti"], righe, num=[1, 2], classi=classi, attr=attr, resp="resp",
                   etichette=["", "Prezzo", "Differenza", "Carenza"],
                   caption=f'Prezzi al pubblico da lista AIFA del {data_lunga(DATA_T)}; in farmacia possono variare per i farmaci di fascia C. '
                           f'«Differenza a carico» = prezzo al pubblico − prezzo di riferimento ({euro(rif)}), come stampata da AIFA. '
                           f'Stato di carenza dall\'elenco AIFA del {data_lunga(DATA_C)}.')
    for r in car:
        for c in CAR[r["aic"]]:
            out += blocco_carenza(c, rim)
    return out + "</section>"


def faq_pa(pa, rim):
    voci, usate = [], set()
    prove = PROVE[pa]
    chiave_pa = nomi.pa_ricerca(pa)
    for k, sugg in sorted(prove.items(), key=lambda kv: (kv[0] != marchio_principale(pa), kv[0] != chiave_pa, kv[0])):
        is_pa = k == chiave_pa
        rr = PA[pa] if is_pa else righe_marchio(pa, k)
        if not rr:
            continue
        nome = pa if is_pa else bello(k)
        nome_up = pa if is_pa else k.upper()
        for tipo, rx in (("eq", TIPO_EQ), ("prezzo", TIPO_PREZZO), ("car", TIPO_CAR)):
            s = next((x for x in sugg if rx.search(x.replace(k, " "))), None)
            if not s or (k, tipo) in usate or len(voci) >= 5:
                continue
            usate.add((k, tipo))
            gr = []
            for r in rr:
                if r["gruppo"] not in gr:
                    gr.append(r["gruppo"])
            if tipo == "eq":
                q = f"Qual è l'equivalente di {nome}?" if not is_pa else f"Quali sono gli equivalenti di {pa.lower()}?"
                parti = []
                for g in gr[:3]:
                    altri = sorted({x["farmaco"] for x in GRUPPI[g] if (is_pa or nomi.marchio(x["farmaco"]) != k or not nomi.di_fantasia(x["farmaco"], x["pa"]))})
                    if is_pa:
                        parti.append(f"{conf_txt(GRUPPI[g][0]['conf_rif'])}: {len(GRUPPI[g])} confezioni, prezzo di riferimento {euro(GRUPPI[g][0]['rif'])}")
                    else:
                        es = ", ".join(altri[:4])
                        n_altri = len(altri)
                        parti.append(f"per la confezione «{conf_txt(GRUPPI[g][0]['conf_rif']).lower()}» il gruppo ha altri {n_altri} nom{'e' if n_altri == 1 else 'i'} commercial{'e' if n_altri == 1 else 'i'}"
                                     + (f" (per esempio {es})" if es else "") + f" e il prezzo di riferimento è {euro(GRUPPI[g][0]['rif'])}")
                resto = (" Gli altri gruppi sono in questa pagina." if len(gr) > 3 else "")
                if is_pa:
                    a = (f"Nella lista di trasparenza AIFA del {data_lunga(DATA_T)} {pa.lower()} ha {len(gr)} grupp{'o' if len(gr) == 1 else 'i'} di equivalenza. "
                         + "; ".join(parti) + "." + resto
                         + f" Le confezioni dello stesso gruppo sono considerate sostituibili da AIFA: {FRASE_FISSA}.")
                else:
                    a = (f"Nella lista di trasparenza AIFA del {data_lunga(DATA_T)} {nome_up} compare in {len(gr)} grupp{'o' if len(gr) == 1 else 'i'}: "
                         + "; ".join(parti) + "." + resto
                         + f" Le confezioni dello stesso gruppo sono considerate sostituibili da AIFA: {FRASE_FISSA}.")
                ref = rim.ref(["trasparenza", "pagina_equivalenti"])
            elif tipo == "prezzo":
                q = f"Quanto costa {nome}?" if not is_pa else f"Quanto costa {pa.lower()}?"
                esempi = sorted(rr, key=lambda r: (r["gruppo"], D(r["prezzo"])))
                if not is_pa:
                    parti = []
                    for g in gr[:3]:
                        xs = [x for x in rr if x["gruppo"] == g]
                        p0, p1 = min(D(x["prezzo"]) for x in xs), max(D(x["prezzo"]) for x in xs)
                        d0, d1 = min(D(x["diff"]) for x in xs), max(D(x["diff"]) for x in xs)
                        pz = euro(p0) if p0 == p1 else f"da {euro(p0)} a {euro(p1)}"
                        dz = ("nessuna differenza da pagare" if d1 == 0 else
                              (f"differenza a carico {euro(d0)}" if d0 == d1 else f"differenza a carico da {euro(d0)} a {euro(d1)}"))
                        parti.append(f"«{conf_txt(GRUPPI[g][0]['conf_rif']).lower()}» {pz} ({dz})")
                    a = (f"Prezzi al pubblico di {nome_up} nella lista AIFA del {data_lunga(DATA_T)}: " + "; ".join(parti) + "."
                         + (" Gli altri gruppi sono in questa pagina." if len(gr) > 3 else "")
                         + " La differenza a carico è la parte che paga chi sceglie questa confezione invece di una al prezzo di riferimento.")
                else:
                    pmin = min(D(x["prezzo"]) for x in rr)
                    pmax = max(D(x["prezzo"]) for x in rr)
                    a = (f"Nella lista AIFA del {data_lunga(DATA_T)} le {len(rr)} confezioni di {pa.lower()} costano da {euro(pmin)} a {euro(pmax)} "
                         f"al pubblico, secondo la confezione. Per ogni gruppo la pagina indica il prezzo di riferimento e la differenza a carico.")
                ref = rim.ref("trasparenza")
            else:
                q = f"{nome} è nell'elenco dei farmaci carenti?"
                cs = [c for r in rr for c in CAR.get(r["aic"], [])]
                if not is_pa:
                    cs += [c for c in carenti_extra(pa) if nomi.marchio(c["nome"]) == k]
                else:
                    cs += carenti_extra(pa)
                if cs:
                    motivi = Counter(c["motivo"] or "motivo non indicato" for c in cs).most_common(2)
                    a = (f"Sì: nell'elenco AIFA del {data_lunga(DATA_C)} ci sono {len(cs)} righe di {nome_up if not is_pa else pa.lower()}"
                         f" (motivo più frequente: {motivi[0][0].lower()}). Le confezioni, le date e gli equivalenti non carenti sono in questa pagina.")
                else:
                    a = (f"No: nell'elenco AIFA del {data_lunga(DATA_C)} non c'è nessuna confezione di {nome_up if not is_pa else pa.lower()}. "
                         "Se in farmacia manca, per AIFA può trattarsi di un'indisponibilità temporanea nella distribuzione locale: il farmacista "
                         "verifica con i grossisti e può chiedere la fornitura diretta al titolare.")
                ref = rim.ref(["carenti", "pagina_carenti"])
            voci.append((q, a, ref, s))
    return voci


def titolo_pa(pa):
    m = marchio_principale(pa)
    cands = []
    if m and sum(1 for x in PA if marchio_principale(x) == m) > 1:
        # stesso nome commerciale per due principi attivi (es. combinazione e principio singolo): il titolo dice quale
        cands += [f"{bello(m)} ({pa.lower()}): equivalenti e prezzi", f"{pa}: equivalenti, prezzi e carenze ({bello(m)})"]
        m = None
    if m:
        cands += [f"{bello(m)} ed equivalenti: prezzi, differenza e carenze", f"{bello(m)}: equivalenti, prezzi e carenze", f"{bello(m)}: equivalenti e prezzi"]
    cands += [f"{pa}: equivalenti, prezzi e carenze", f"{pa}: equivalenti e prezzi", pa[:60]]
    for t in cands:
        if len(t) <= 65:
            return t
    raise SystemExit(f"titolo troppo lungo: {pa}")


def descr_pa(pa, info):
    m = marchio_principale(pa)
    car = f"; {info['n_car']} carenti al {data_breve(DATA_C)}" if info["n_car"] else "; nessuna carente al " + data_breve(DATA_C)
    pre = f"{bello(m)} ({pa.lower()})" if m else pa
    cands = [f"{pre}: {info['n_conf']} confezioni in {info['n_gr']} gruppi AIFA, prezzo di riferimento e differenza da pagare{car}.",
             f"{pre}: {info['n_conf']} confezioni nella lista AIFA, differenza fino a {euro(info['max_diff'])}{car}.",
             f"{pa}: {info['n_conf']} confezioni nella lista AIFA del {data_breve(DATA_T)}{car}.",
             f"{pa[:90]}: lista AIFA del {data_breve(DATA_T)} e carenze al {data_breve(DATA_C)}."]
    for t in cands:
        if 70 <= len(t) <= 160:
            return t
    for t in cands:
        if len(t) <= 160:
            return (t + " Equivalenti e prezzi.")[:160] if len(t) < 70 else t
    raise SystemExit(f"descrizione fuori misura: {pa}")


def info_pa(pa):
    rr = PA[pa]
    return {"n_conf": len(rr), "n_gr": len(gruppi_pa(pa)), "n_car": sum(1 for r in rr if carente(r["aic"])),
            "max_diff": max(D(r["diff"]) for r in rr), "n_zero": sum(1 for r in rr if D(r["diff"]) == 0),
            "n_extra": len(carenti_extra(pa))}


def pagina_pa(pa):
    rim = Rimandi()
    info = info_pa(pa)
    gr = gruppi_pa(pa)
    gr.sort(key=lambda g: (conf_txt(GRUPPI[g][0]["conf_rif"]).lower()))
    m = marchio_principale(pa)
    indicizza = INDICIZZA[pa]
    sub = (f"{num(info['n_conf'])} confezioni in {info['n_gr']} grupp{'o' if info['n_gr'] == 1 else 'i'} di equivalenza della lista di trasparenza AIFA del "
           f"<strong>{data_lunga(DATA_T)}</strong>, con lo stato di carenza dell'elenco AIFA del <strong>{data_lunga(DATA_C)}</strong>.")
    eyebrow = "Principio attivo · ATC " + ", ".join(atc_pa(pa))
    titolo_h1 = f"{pa}: equivalenti, prezzo di riferimento e carenze"
    testata = banda(eyebrow, titolo_h1, sub)
    cifre = (f'<div class="card cifre pull">'
             f'<div class="cifra main"><b>{num(info["n_conf"])}</b><span>confezioni nella lista di trasparenza</span></div>'
             f'<div class="cifra"><b>{num(info["n_zero"])}</b><span>senza differenza da pagare</span></div>'
             f'<div class="cifra"><b>{euro(info["max_diff"]) if info["max_diff"] > 0 else "0,00 €"}</b><span>differenza più alta a carico</span></div>'
             f'<div class="cifra"><b>{num(info["n_car"])}</b><span>confezioni nell\'elenco carenti</span></div>'
             f'<p class="asof">{ico("check")} Lista di trasparenza AIFA del {data_lunga(DATA_T)}{rim.ref("trasparenza")}, elenco carenti del {data_lunga(DATA_C)}{rim.ref("carenti")}. '
             f'Controllato il {data_lunga(CONTROLLO)}.</p></div>')
    corpo = cifre
    marchi = sorted({r["farmaco"] for r in PA[pa] if nomi.di_fantasia(r["farmaco"], r["pa"])})
    corpo += '<div class="testo">'
    corpo += (f'<p>Ogni blocco qui sotto è un gruppo di equivalenza AIFA: stesse caratteristiche della confezione di riferimento (principio attivo, '
              f'forma, dosaggio, numero di unità). Le confezioni dello stesso gruppo sono considerate sostituibili, salvo diversa decisione di AIFA, '
              f'e il Servizio sanitario le rimborsa fino al prezzo di riferimento: se si sceglie una confezione con prezzo più alto, la differenza è a '
              f'carico di chi la compra.{rim.ref(["pagina_equivalenti", "legge_art7"])}</p>')
    if m:
        rm = righe_marchio(pa, m)
        n_g = len({r["gruppo"] for r in rm})
        conf_s = "confezione" if len(rm) == 1 else "confezioni"
        gr_s = "gruppo" if n_g == 1 else "gruppi"
        corpo += f'<p>{h(m.upper())} è uno dei nomi commerciali di {h(pa.lower())}: nella lista compare con {len(rm)} {conf_s}, in {n_g} {gr_s}.</p>'
    if marchi:
        corpo += (f'<p class="small">Nomi commerciali nella lista ({len(marchi)}): {h(", ".join(marchi[:40]))}'
                  + (f" e altri {len(marchi) - 40}" if len(marchi) > 40 else "") + ".</p>")
    corpo += "</div>"
    if len(gr) > 1:
        corpo += ('<h2 id="gruppi">I gruppi di equivalenza</h2><ul class="indice">' + "".join(
            f'<li><a href="#g-{g.lower()}">{h(conf_txt(GRUPPI[g][0]["conf_rif"]))}</a><span class="small">{len(GRUPPI[g])} conf.'
            + (f', {sum(1 for r in GRUPPI[g] if carente(r["aic"]))} carenti' if any(carente(r["aic"]) for r in GRUPPI[g]) else "") + "</span></li>" for g in gr) + "</ul>")
    for i, g in enumerate(gr):
        corpo += sezione_gruppo(g, rim)
        if i == 0 and indicizza:
            corpo += AD
    extra = carenti_extra(pa)
    if extra:
        corpo += (f'<h2 id="altre-carenze">Altre confezioni carenti con lo stesso codice ATC</h2><p>Queste confezioni sono nell\'elenco AIFA dei '
                  f'farmaci carenti del {data_lunga(DATA_C)} ma non nella lista di trasparenza (per esempio farmaci ospedalieri, di fascia C '
                  f'o con un\'altra forma): non hanno un prezzo di riferimento.{rim.ref("carenti")}</p>')
        rr_ = []
        for c in extra:
            rr_.append([f'<strong>{h(c["nome"])}</strong><small>{h(c["confezione"])}</small><small>{h(c["titolare"])} · AIC {c["aic"]}</small>',
                        f'{h(stato_carenza(c))}', data_breve(c["fine_presunta"]) or "—", h(c["motivo"] or "—"), h(c["classe"])])
        corpo += tabella(["Medicinale", "Carenza", "Fine presunta", "Motivo", "Classe"], rr_, resp="resp",
                         attr=[f' data-aic="{c["aic"]}" data-carente="1"' for c in extra], classi=["carente"] * len(extra))
    voci = faq_pa(pa, rim)
    fh, fld = faq_html([(q, a, ref) for q, a, ref, _ in voci])
    corpo += fh
    corpo += ('<h2 id="cosa-fare">Se il farmaco manca in farmacia</h2><div class="testo"><p>Se una confezione è nell\'elenco dei carenti, AIFA indica '
              f'cosa fare nella colonna «Suggerimenti»; se non c\'è, può trattarsi di un problema locale di distribuzione. I passi indicati da AIFA sono '
              f'nella pagina <a href="/farmaco-mancante/">farmaco che non si trova in farmacia</a>. Per scegliere o cambiare farmaco, {FRASE_FISSA}.'
              f'{rim.ref("pagina_mancante")}</p></div>')
    corpo += rim.elenco()
    ld = [x for x in [fld] if x]
    titolo = titolo_pa(pa)
    pagina(SLUG[pa] + "/", titolo, descr_pa(pa, info), corpo, testata,
           briciole=[("Home", ""), (pa, SLUG[pa] + "/")], jsonld=ld, indicizza=indicizza)
    return voci


# ---------------------------------------------------------------- elenco dei farmaci carenti
ETICHETTA_SUGG = [
    ("Per trattamento alternativo si consiglia di rivolgersi allo specialista o al M", "Rivolgersi al medico"),
    ("Si rilascia autorizzazione all’importazione alle strutture sanitarie", "Importazione per le strutture sanitarie"),
    ("Rilasciata determinazione per l’importazione al titolare", "Importato dal titolare AIC"),
]


def etichetta_sugg(s):
    for pre, et in ETICHETTA_SUGG:
        if s.startswith(pre):
            return et
    return "Altro (vedi AIFA)" if s else "—"


def carenze():
    rim = Rimandi()
    rr = sorted(CA["righe"], key=lambda c: (c["nome"], c["aic"]))
    corpo_righe = []
    for c in rr:
        t = AIC_T.get(c["aic"])
        link = f'<small><a href="/{SLUG[t["pa"]]}/#aic-{c["aic"]}">equivalenti e prezzi</a></small>' if t else ""
        eq = c["equivalente"].lower().startswith("s")
        prev = ' <small>prevista</small>' if c["inizio"] and c["inizio"] > CA["pubblicato_il"] else ""
        celle = [f'<td><strong>{h(c["nome"])}</strong><small>{h(c["confezione"])}</small><small>AIC {c["aic"]} · {h(c["classe"].lower())}</small>{link}</td>',
                 f'<td data-l="Principio attivo">{h(c["pa"].lower())}</td>',
                 f'<td data-l="Inizio" data-v="{c["inizio"] or ""}">{data_breve(c["inizio"]) or "—"}{prev}</td>',
                 f'<td data-l="Fine presunta" data-v="{c["fine_presunta"] or "9999"}">{data_breve(c["fine_presunta"]) or "—"}</td>',
                 f'<td data-l="Motivo">{h(c["motivo"] or "—")}</td>', f'<td data-l="Equivalente">{"Sì" if eq else "No"}</td>',
                 f'<td data-l="Indicazione AIFA">{h(etichetta_sugg(c["suggerimenti"]))}</td>']
        corpo_righe.append(f'<tr data-aic="{c["aic"]}" data-eq="{1 if eq else 0}" data-inizio="{c["inizio"] or ""}" data-fine="{c["fine_presunta"] or ""}">' + "".join(celle) + "</tr>")
    cols = ["Medicinale", "Principio attivo", "Inizio", "Fine presunta", "Motivo", "Equivalente", "Indicazione AIFA"]
    intest = "".join(f'<th scope="col" data-col="{i}"><button type="button">{x}</button></th>' for i, x in enumerate(cols))
    corpo_tab = (f'<div class="tab"><table class="dati resp7" id="elenco-carenti"><thead><tr>{intest}</tr></thead><tbody>{"".join(corpo_righe)}</tbody></table></div>')
    mot = Counter(c["motivo"] or "non indicato" for c in CA["righe"]).most_common(6)
    sub = (f"L'elenco ufficiale AIFA aggiornato al <strong>{data_lunga(DATA_C)}</strong>: {NUM['n_car']} confezioni, {NUM['n_car_pa']} principi attivi. "
           "Filtra per nome, ordina per data e trova gli equivalenti non carenti.")
    testata = banda("Elenco AIFA dei farmaci carenti", f"Farmaci carenti: elenco AIFA del {data_lunga(DATA_C)}", sub, icona="alert")
    corpo = (f'<div class="card cifre pull"><div class="cifra main"><b>{NUM["n_car"]}</b><span>confezioni nell\'elenco</span></div>'
             f'<div class="cifra"><b>{NUM["n_car_eq"]}</b><span>con equivalente secondo AIFA</span></div>'
             f'<div class="cifra"><b>{NUM["n_car_t"]}</b><span>anche nella lista di trasparenza</span></div>'
             f'<div class="cifra"><b>{NUM["n_car_t_eq"]}</b><span>con un equivalente non carente nello stesso gruppo</span></div>'
             f'<p class="asof">{ico("check")} Elenco AIFA dei farmaci carenti aggiornato al {data_lunga(DATA_C)}{rim.ref("carenti")}; '
             f'gruppi dalla lista di trasparenza del {data_lunga(DATA_T)}{rim.ref("trasparenza")}.</p></div>')
    corpo += ('<div class="testo"><p>Per AIFA un farmaco è «carente» quando il titolare dell\'autorizzazione non riesce a garantirne la fornitura in tutta '
              f'Italia. L\'elenco indica la data di inizio, la fine presunta (se il titolare l\'ha comunicata), il motivo e cosa suggerisce AIFA.{rim.ref("pagina_carenti")} '
              'Se la fine presunta è passata, il farmaco resta nell\'elenco finché il titolare non comunica la fine effettiva della carenza.</p>'
              f'<p>Motivi più frequenti: ' + "; ".join(f"{h(k.lower())} {num(v)}" for k, v in mot) + '.</p></div>')
    corpo += AD
    corpo += (f'<section data-tabella aria-labelledby="tab-h"><h2 id="tab-h">L\'elenco completo</h2>'
              '<div class="filtri"><label for="filtro" class="hp">Filtra l\'elenco</label><input id="filtro" type="search" data-filtro placeholder="Filtra: nome, principio attivo, motivo…" autocomplete="off">'
              '<label class="check"><input type="checkbox" data-solo-eq> Solo con equivalente</label></div>'
              f'<p class="conteggio" data-conteggio aria-live="polite">{NUM["n_car"]} confezioni</p>' + corpo_tab +
              '<p class="vuoto-ricerca" data-vuoto hidden>Nessuna confezione con questo filtro. Se il tuo farmaco non c\'è, per AIFA non è una carenza ufficiale: '
              'vedi <a href="/farmaco-mancante/">farmaco che non si trova</a>.</p></section>')
    corpo += ('<h2 id="legenda">Come leggere le colonne</h2><div class="testo"><ul>'
              '<li><strong>Equivalente</strong>: «Sì» se AIFA indica che sul mercato italiano esiste un medicinale equivalente.</li>'
              '<li><strong>Indicazione AIFA</strong>: forma breve della colonna «Suggerimenti/Indicazioni AIFA». «Rivolgersi al medico» = «Per trattamento alternativo si consiglia di rivolgersi allo specialista o al M.M.G»; '
              '«Importazione per le strutture sanitarie» = «Si rilascia autorizzazione all’importazione alle strutture sanitarie per analogo autorizzato all’estero»; '
              '«Importato dal titolare AIC» = «Rilasciata determinazione per l’importazione al titolare A.I.C.». Il testo completo è nella pagina di ogni principio attivo.</li>'
              '<li><strong>prevista</strong> accanto alla data di inizio: la carenza è già annunciata ma comincia dopo la data dell\'elenco.</li>'
              '<li>Il link «equivalenti e prezzi» porta al gruppo della lista di trasparenza, con le confezioni non carenti e la differenza da pagare.</li></ul></div>')
    voci = faq_fisse("carenze", rim)
    fh, fld = faq_html(voci)
    corpo += fh + rim.elenco()
    pagina("carenze/", f"Farmaci carenti: elenco AIFA del {data_breve(DATA_C)}",
           f"Elenco AIFA dei farmaci carenti del {data_breve(DATA_C)}: {NUM['n_car']} confezioni con inizio, fine presunta, motivo ed equivalenti non carenti.",
           corpo, testata, briciole=[("Home", ""), ("Farmaci carenti", "carenze/")], jsonld=[x for x in [fld] if x])


# ---------------------------------------------------------------- guida: farmaco che non si trova
def farmaco_mancante():
    rim = Rimandi()
    testata = banda("Guida con le indicazioni AIFA", "Farmaco che non si trova in farmacia: carenza o indisponibilità",
                    "Cosa dice AIFA quando un medicinale manca: come capire se è una carenza ufficiale e quali passi sono previsti.", icona="alert")
    r_ = rim.ref("pagina_mancante")
    corpo = (f'<div class="card pull testo"><p style="margin:0"><strong>Prima di tutto: controlla se il farmaco è nell\'elenco ufficiale.</strong> '
             f'Per AIFA un medicinale può mancare per due motivi diversi, carenza e indisponibilità, che richiedono interventi diversi.{r_} '
             f'L\'elenco del {data_lunga(DATA_C)} è nella pagina <a href="/carenze/">farmaci carenti</a>, con un filtro per nome.</p></div>')
    corpo += '<h2 id="carenza">1. Se il farmaco è nell\'elenco dei carenti</h2><div class="testo">'
    corpo += (f'<p>AIFA chiede di indirizzare i pazienti secondo le indicazioni della lista. Nell\'elenco del {data_lunga(DATA_C)} le indicazioni sono queste:{r_}</p><ul>')
    cnt = Counter(etichetta_sugg(c["suggerimenti"]) for c in CA["righe"])
    corpo += (f'<li><strong>«Per trattamento alternativo si consiglia di rivolgersi allo specialista o al medico di medicina generale»</strong> '
              f'({num(cnt["Rivolgersi al medico"])} confezioni): ci sono equivalenti o alternative che il medico può valutare.</li>'
              f'<li><strong>«Si rilascia autorizzazione all’importazione alle strutture sanitarie per analogo autorizzato all’estero»</strong> '
              f'({num(cnt["Importazione per le strutture sanitarie"])}): l\'importazione la attiva il medico ed è gestita da farmacie ospedaliere o ASL.</li>'
              f'<li><strong>«Rilasciata determinazione per l’importazione al titolare AIC»</strong> ({num(cnt["Importato dal titolare AIC"])}): il farmaco importato '
              'si ritira dalla farmacia ospedaliera o dall\'ASL, con la ricetta.</li></ul>')
    corpo += ('<p>Secondo AIFA le confezioni importate, anche se per la terapia a casa, non si ritirano nelle farmacie convenzionali ma solo da ASL o strutture '
              f'indicate dal territorio, salvo diverse scelte della Regione.{r_}</p></div>')
    corpo += AD
    corpo += '<h2 id="indisponibilita">2. Se il farmaco non è nell\'elenco</h2><div class="testo">'
    corpo += (f'<p>Allora non è una carenza ufficiale: per AIFA può trattarsi di un\'indisponibilità temporanea, cioè di un problema locale della distribuzione.{rim.ref("pagina_carenti")} '
              f'In questo caso il farmacista contatta almeno tre grossisti della sua zona per verificare che il farmaco manchi davvero. Se manca, può chiederlo '
              f'direttamente al titolare: la legge obbliga il titolare a fornire entro 48 ore, su richiesta delle farmacie, un medicinale che non si trova nella '
              f'rete di distribuzione regionale (art. 105, comma 4, del decreto legislativo 219/2006).{r_}</p>'
              f'<p>Il farmacista può anche segnalare la mancanza alla Regione, che verifica presso altri grossisti.{rim.ref("pagina_carenti")}</p></div>')
    corpo += '<h2 id="equivalenti">3. Gli equivalenti dello stesso gruppo</h2><div class="testo">'
    corpo += (f'<p>Molti farmaci carenti hanno un equivalente non carente. Nell\'elenco del {data_lunga(DATA_C)}, {NUM["n_car_t"]} confezioni carenti sono anche nella '
              f'lista di trasparenza: per {NUM["n_car_t_eq"]} di queste nello stesso gruppo di equivalenza c\'è almeno una confezione che non è nell\'elenco dei '
              f'carenti.{rim.ref(["carenti", "trasparenza"])} Nelle pagine dei principi attivi trovi quali sono, con la differenza di prezzo.</p>'
              f'<p>Se il medico ha scritto «non sostituibile» sulla ricetta, il farmacista non può sostituire il farmaco con uno uguale a prezzo più basso '
              f'(art. 7, comma 2, del decreto-legge 347/2001).{rim.ref("legge_art7")} In ogni caso la scelta del farmaco non la fa questo sito: {FRASE_FISSA}.</p></div>')
    # i principi attivi con più confezioni carenti nella lista di trasparenza
    top = Counter(AIC_T[a]["pa"] for a in CAR_IN_T_AIC).most_common(12)
    corpo += '<h2 id="piu-carenti">Principi attivi con più confezioni carenti</h2>'
    corpo += tabella(["Principio attivo", "Confezioni carenti", "Confezioni nella lista"],
                     [[f'<a href="/{SLUG[p]}/">{h(p)}</a>', num(n), num(len(PA[p]))] for p, n in top], num=[1, 2], resp="resp",
                     etichette=["", "Carenti", "Nella lista"], caption=f"Confezioni della lista di trasparenza del {data_lunga(DATA_T)} presenti nell'elenco carenti del {data_lunga(DATA_C)}.")
    voci = faq_fisse("farmaco-mancante", rim)
    fh, fld = faq_html(voci)
    corpo += fh + rim.elenco()
    pagina("farmaco-mancante/", "Farmaco che non si trova in farmacia: cosa dice AIFA",
           "Farmaco che manca in farmacia: come capire se è una carenza ufficiale AIFA o un'indisponibilità locale, e i passi previsti per importazione e fornitura diretta.",
           corpo, testata, briciole=[("Home", ""), ("Farmaco che non si trova", "farmaco-mancante/")], jsonld=[x for x in [fld] if x])


# ---------------------------------------------------------------- indice di ricerca (JSON) e home
def indice_ricerca():
    voci, visti = [], set()
    for p in sorted(PA):
        voci.append([p, f"principio attivo · {len(PA[p])} confezioni", f"/{SLUG[p]}/", ""])
    for r in sorted(RIGHE, key=lambda r: r["farmaco"]):
        k = (r["farmaco"], r["pa"])
        if k in visti:
            continue
        visti.add(k)
        voci.append([r["farmaco"], r["pa"].lower(), f"/{SLUG[r['pa']]}/", ""])
    for c in sorted(CA["righe"], key=lambda c: c["nome"]):
        if c["aic"] in AIC_T:
            continue
        k = (c["nome"], "car")
        if k in visti:
            continue
        visti.add(k)
        voci.append([c["nome"], "nell'elenco carenti · " + c["pa"].lower(), "/carenze/?q=" + re.sub(r"\s+", "+", c["nome"].lower()), c["pa"]])
    return json.dumps(voci, ensure_ascii=False, separators=(",", ":"))


INDICE = indice_ricerca()
INDICE_FILE = f"indice.{_impronta(INDICE)}.json"


def home():
    rim = Rimandi()
    cerca = (f'<form class="cerca" role="search"><label for="q" class="hp">Cerca un farmaco</label>'
             f'<input id="q" type="search" data-cerca data-indice="/assets/{INDICE_FILE}" placeholder="Nome del farmaco o principio attivo: Augmentin, atorvastatina…" autocomplete="off"></form>'
             '<ul class="risultati" data-risultati hidden aria-live="polite"></ul>')
    testata = banda("Liste ufficiali AIFA", "Farmaco equivalente: prezzi, differenza da pagare e carenze",
                    f"Cerca un farmaco: vedi gli equivalenti dello stesso gruppo, il prezzo di riferimento, quanto paghi in più con la marca e se è "
                    f"nell'elenco dei carenti. Lista di trasparenza del <strong>{data_lunga(DATA_T)}</strong>, carenti del <strong>{data_lunga(DATA_C)}</strong>.",
                    extra=cerca)
    corpo = (f'<div class="card cifre pull"><div class="cifra main"><b>{NUM["n_conf"]}</b><span>confezioni nella lista di trasparenza</span></div>'
             f'<div class="cifra"><b>{NUM["n_gruppi"]}</b><span>gruppi di equivalenza</span></div>'
             f'<div class="cifra"><b>{NUM["n_diff"]}</b><span>confezioni con una differenza da pagare</span></div>'
             f'<div class="cifra"><b>{NUM["n_car"]}</b><span>confezioni nell\'elenco carenti</span></div>'
             f'<p class="asof">{ico("check")} Lista di trasparenza AIFA del {data_lunga(DATA_T)}{rim.ref("trasparenza")}, elenco dei farmaci carenti '
             f'del {data_lunga(DATA_C)}{rim.ref("carenti")}. Controllato il {data_lunga(CONTROLLO)}.</p></div>')
    corpo += '<h2 id="come-funziona">Come funzionano equivalenti e prezzo di riferimento</h2><div class="testo">'
    corpo += (f'<p>Un farmaco equivalente ha lo stesso principio attivo, la stessa forma, via di somministrazione, modalità di rilascio, dosaggio e numero '
              f'di unità di un farmaco di riferimento con il brevetto scaduto; sulla confezione c\'è la scritta «Medicinale Equivalente».{rim.ref("pagina_equivalenti")} '
              f'AIFA mette questi farmaci nella <strong>lista di trasparenza</strong>, divisi in gruppi: dentro un gruppo le confezioni sono considerate '
              f'sostituibili, salvo diversa decisione di AIFA.{rim.ref("pagina_trasparenza")}</p>')
    corpo += ('<p>La regola del prezzo è nell\'articolo 7 del decreto-legge 18 settembre 2001, n. 347, convertito dalla legge 16 novembre 2001, n. 405:</p>'
              '<blockquote class="legge">«I medicinali, aventi uguale composizione in principi attivi, nonché forma farmaceutica, via di somministrazione, modalità '
              'di rilascio, numero di unità posologiche e dosi unitarie uguali, sono rimborsati al farmacista dal Servizio sanitario nazionale fino alla concorrenza '
              'del prezzo più basso del corrispondente prodotto disponibile nel normale ciclo distributivo regionale, sulla base di apposite direttive definite '
              f'dalla regione»<cite>Art. 7, comma 1, testo vigente su Normattiva{rim.ref("legge_art7")}</cite></blockquote>'
              '<blockquote class="legge">«Qualora il medico apponga sulla ricetta l\'indicazione di cui al comma 2, con cui ritiene il farmaco prescritto insostituibile '
              'ovvero l\'assistito non accetti la sostituzione proposta dal farmacista, ai sensi del comma 3, la differenza fra il prezzo più basso ed il prezzo del '
              f'farmaco prescritto è a carico dell\'assistito con l\'eccezione dei pensionati di guerra titolari di pensioni vitalizie.»<cite>Art. 7, comma 4{rim.ref("legge_art7")}</cite></blockquote>')
    corpo += (f'<p>In pratica: ogni gruppo ha un <strong>prezzo di riferimento</strong>, quello che il Servizio sanitario rimborsa. Se in farmacia prendi una '
              f'confezione che costa di più, paghi tu la <strong>differenza</strong>. AIFA la stampa per ogni confezione: nella lista del {data_lunga(DATA_T)} '
              f'{NUM["n_diff"]} confezioni su {NUM["n_conf"]} hanno una differenza maggiore di zero. Le Regioni applicano la lista con direttive proprie '
              f'(comma 1), quindi in farmacia possono esserci regole regionali in più. Per la scelta del farmaco, {FRASE_FISSA}.</p></div>')
    corpo += AD
    # carenze: principi attivi con più confezioni carenti che hanno equivalenti non carenti
    top = Counter(AIC_T[a]["pa"] for a in CON_EQ_NON_CAR).most_common(10)
    corpo += (f'<h2 id="carenze">Farmaci carenti con un equivalente non carente</h2><p>Nell\'elenco AIFA del {data_lunga(DATA_C)} ci sono {NUM["n_car"]} confezioni; '
              f'{NUM["n_car_t"]} sono anche nella lista di trasparenza e per {NUM["n_car_t_eq"]} esiste nello stesso gruppo almeno una confezione non carente. '
              f'I principi attivi con più casi:{rim.ref(["carenti", "trasparenza"])}</p>')
    corpo += tabella(["Principio attivo", "Carenti con equivalente non carente", "Confezioni nella lista"],
                     [[f'<a href="/{SLUG[p]}/">{h(p)}</a>', num(n), num(len(PA[p]))] for p, n in top], num=[1, 2], resp="resp",
                     etichette=["", "Carenti con equivalente", "Nella lista"])
    corpo += '<p><a class="btn" href="/carenze/">Tutto l\'elenco dei farmaci carenti</a></p>'
    # differenze più alte
    alte = sorted(RIGHE, key=lambda r: (-D(r["diff"]), r["farmaco"]))[:10]
    corpo += (f'<h2 id="differenze">Le differenze da pagare più alte</h2><p>Le dieci confezioni con la differenza a carico più alta nella lista del {data_lunga(DATA_T)}: '
              f'è quanto si paga in più rispetto al prezzo di riferimento del gruppo.{rim.ref("trasparenza")}</p>')
    corpo += tabella(["Farmaco", "Prezzo al pubblico", "Prezzo di riferimento", "Differenza"],
                     [[f'<a href="/{SLUG[r["pa"]]}/#aic-{r["aic"]}">{h(r["farmaco"])}</a><small>{h(r["pa"])}</small><small>{h(r["confezione"])}</small>', euro(r["prezzo"]),
                       euro(r["rif"]), euro(r["diff"])] for r in alte], num=[1, 2, 3], resp="resp", etichette=["", "Prezzo", "Riferimento", "Differenza"],
                     caption=f"Prezzi al pubblico da lista AIFA del {data_lunga(DATA_T)}; in farmacia possono variare per i farmaci di fascia C.")
    # indice A-Z
    lettere = defaultdict(list)
    for p in sorted(PA, key=lambda x: nomi.slug(x)):
        lettere[nomi.slug(p)[0].upper()].append(p)
    corpo += (f'<h2 id="indice">Tutti i principi attivi ({NUM["n_pa"]})</h2><p class="small">Ogni pagina ha i gruppi di equivalenza, i prezzi e lo stato '
              'di carenza di ogni confezione. Il numero indica le confezioni nella lista.</p>')
    for L, ps in lettere.items():
        corpo += (f'<h3>{L}</h3><ul class="indice">' + "".join(f'<li><a href="/{SLUG[p]}/">{h(p)}</a><span class="small">{len(PA[p])}</span></li>' for p in ps) + "</ul>")
    voci = faq_fisse("home", rim)
    fh, fld = faq_html(voci)
    corpo += fh + rim.elenco()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/", "inLanguage": "it"}] + ([fld] if fld else [])
    pagina("", "Farmaco equivalente: prezzi, differenza e carenze AIFA",
           f"Equivalenti, prezzo di riferimento e differenza da pagare per {NUM['n_conf']} confezioni della lista AIFA, con i farmaci carenti del {data_breve(DATA_C)}.",
           corpo, testata.replace("{bc}", ""), jsonld=ld)


# ---------------------------------------------------------------- pagine del sito
MODULO = """<form name="segnalazioni" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card">
<input type="hidden" name="form-name" value="segnalazioni">
<p class="hp"><label>Lascia vuoto questo campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Pagina o farmaco<input type="text" name="pagina" required maxlength="300" placeholder="Per esempio /amoxicillina/"></label>
<label>Cosa non torna con l'elenco AIFA?<textarea name="messaggio" required rows="5" maxlength="3000"></textarea></label>
<label>Fonte ufficiale (facoltativa)<input type="url" name="fonte" maxlength="500" placeholder="https://"></label>
<label>La tua email (facoltativa, solo se vuoi una risposta)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>Accetto che il messaggio, e l'email se l'ho scritta, siano conservati per controllare e rispondere alla segnalazione (vedi la <a href="/privacy/#segnalazioni">privacy</a>). Non scrivo dati sulla mia salute.</span></label>
<button type="submit" class="btn">Invia la segnalazione</button>
</form>"""


def come_lavoriamo(n_index, n_noindex, n_faq):
    rim = Rimandi()
    A = carica("classe_a.json")["aic"]
    in_a = sum(1 for r in RIGHE if r["aic"] in A)
    uguali = sum(1 for r in RIGHE if r["aic"] in A and A[r["aic"]]["prezzo"] == r["prezzo"])
    corpo = (f'<div class="card pull"><p style="margin:0"><strong>Usiamo solo gli elenchi ufficiali di AIFA, con la loro data.</strong> Non aggiungiamo prezzi presi '
             f'da altre fonti, non diamo consigli e non diciamo quale farmaco prendere: per questo, {FRASE_FISSA}.</p></div>')
    corpo += '<h2 id="fonti-usate">Gli elenchi che usiamo</h2>'
    rr = []
    for fid, f in FJ["file"].items():
        rr.append([f'<a href="{h(f["pagina"])}" rel="noopener">{h(f["titolo"])}</a>{rim.ref(fid)}', data_lunga(f["pubblicato_il"]), data_lunga(f["letto_il"]),
                   num(f["byte"]), f'<code>{f["sha256"][:12]}</code>'])
    corpo += tabella(["Elenco AIFA", "Pubblicato il", "Letto il", "Byte", "Impronta"], rr, num=[3],
                     caption="L'impronta (SHA-256, prime 12 cifre) identifica il file letto: se AIFA pubblica un file nuovo, cambia l'impronta e rifacciamo i controlli.")
    corpo += (f'<p class="small">Licenza: AIFA distribuisce i dati aperti con licenza Creative Commons Attribuzione 4.0 (CC BY 4.0), che permette il riuso '
              f'anche commerciale con l\'obbligo di citare la fonte.{rim.ref("open_data")} Questo sito cita AIFA in ogni pagina; la presentazione, i conteggi e '
              'gli incroci tra gli elenchi sono nostri.</p>')
    corpo += '<h2 id="metodo">Cosa facciamo con i dati</h2><div class="testo"><ol>'
    corpo += (f'<li><strong>Lista di trasparenza.</strong> Riportiamo per ogni confezione prezzo al pubblico, prezzo di riferimento e differenza a carico così come '
              f'li stampa AIFA. Il controllo automatico verifica su tutte le {NUM["n_conf"]} righe che differenza = prezzo al pubblico − prezzo di riferimento.</li>'
              f'<li><strong>Farmaci carenti.</strong> Una confezione è «carente» nel sito solo se il suo codice AIC è nell\'elenco AIFA del {data_lunga(DATA_C)}. '
              'Data di inizio, fine presunta, motivo, suggerimenti e note sono quelli di AIFA, parola per parola.</li>'
              '<li><strong>Equivalenti non carenti.</strong> Sono le confezioni dello stesso gruppo della lista di trasparenza il cui codice AIC non è nell\'elenco dei carenti. '
              'Non sappiamo se sono disponibili in una farmacia precisa: l\'elenco non lo dice.</li>'
              '<li><strong>Altre confezioni carenti con lo stesso codice ATC.</strong> Righe dell\'elenco carenti che non sono nella lista di trasparenza: le mostriamo '
              'nella pagina del principio attivo con lo stesso codice ATC, senza prezzo.</li>'
              f'<li><strong>Controllo incrociato.</strong> Delle {NUM["n_conf"]} confezioni della lista di trasparenza, {num(in_a)} sono anche nell\'elenco dei farmaci '
              f'di fascia A del {data_lunga(FJ["file"]["classe_a"]["pubblicato_il"])}; per {num(uguali)} il prezzo al pubblico è identico (gli altri prezzi sono '
              f'cambiati tra le due date).{rim.ref("classe_a")}</li></ol></div>')
    corpo += '<h2 id="pagine">Quali pagine pubblichiamo</h2><div class="testo">'
    corpo += (f'<p>Una pagina per ogni principio attivo della lista ({NUM["n_pa"]}), con un blocco per ogni gruppo di equivalenza. Le cerchiamo nei suggerimenti '
              f'di ricerca di Google: {n_index} pagine hanno ricerche vere su equivalente, generico, prezzo o carenza (del principio attivo o di un suo nome '
              f'commerciale) e sono indicizzate; le altre {n_noindex} restano consultabili dalla ricerca del sito ma chiediamo ai motori di non indicizzarle, '
              f'e non hanno pubblicità. Le {n_faq} domande frequenti delle pagine nascono da quelle ricerche.</p></div>')
    corpo += '<h2 id="cosa-non-facciamo">Cosa non facciamo</h2><div class="testo"><ul>'
    corpo += ('<li>Non diamo consigli medici, non facciamo diagnosi e non suggeriamo di cambiare farmaco.</li>'
              '<li>Non vendiamo farmaci e non pubblichiamo pubblicità o link di affiliazione per farmaci con obbligo di ricetta.</li>'
              '<li>Non diciamo in quale farmacia un farmaco è disponibile: gli elenchi AIFA non lo dicono.</li>'
              '<li>Non calcoliamo eventuali ticket o quote regionali: dipendono dalla Regione.</li></ul></div>')
    corpo += '<h2 id="aggiornamenti">Ogni quanto aggiorniamo</h2><div class="testo"><ul>'
    corpo += ('<li><strong>Lista di trasparenza</strong>: AIFA la pubblica ogni mese. La ricarichiamo dopo l\'uscita.</li>'
              '<li><strong>Elenco dei farmaci carenti</strong>: AIFA lo aggiorna almeno due volte alla settimana; noi lo ricarichiamo ogni settimana. '
              'La data dell\'elenco usato è scritta in ogni pagina.</li>'
              '<li>Ogni aggiornamento rifà tutti i controlli: impronta dei file, intestazioni delle colonne, differenze, stati di carenza, pagine.</li></ul></div>')
    corpo += ('<h2 id="segnala">Segnala un errore</h2><p>Hai trovato una riga diversa dall\'elenco AIFA? Scrivici la pagina e, se puoi, il link alla fonte. '
              'Controlliamo sull\'elenco ufficiale. L\'email è facoltativa. Non scrivere dati sulla tua salute.</p>' + MODULO)
    corpo += rim.elenco()
    testata = banda("Come lavoriamo", "Come leggiamo e controlliamo gli elenchi AIFA",
                    "Quali file usiamo, con che data, cosa incrociamo, quali pagine indicizziamo e ogni quanto aggiorniamo.", corta=True, icona="shield")
    pagina("come-lavoriamo/", "Come lavoriamo: elenchi AIFA, controlli e aggiornamenti",
           "Come Farmaco Equivalente usa la lista di trasparenza e l'elenco dei farmaci carenti di AIFA: date, impronte dei file, controlli e aggiornamenti.",
           corpo, testata, briciole=[("Home", ""), ("Come lavoriamo", "come-lavoriamo/")])


def chi_siamo():
    corpo = ('<div class="card pull testo"><p><strong>Farmaco Equivalente è un sito informativo indipendente e gratuito.</strong> Mette in pagine semplici la '
             'lista di trasparenza e l\'elenco dei farmaci carenti di AIFA, principio attivo per principio attivo, con la data di ogni elenco.</p></div>'
             '<h2>Perché esiste</h2><div class="testo"><p>Gli elenchi ufficiali sono file con migliaia di righe. Chi cerca «equivalente di…» o «… non si trova in '
             'farmacia» deve aprire due file diversi e incrociarli a mano: qui lo trova già fatto, con la fonte accanto.</p></div>'
             '<h2>Cosa non siamo</h2><div class="testo"><ul><li>Non siamo AIFA, il Ministero della Salute, una farmacia o un\'azienda farmaceutica, e non siamo '
             'affiliati a nessuno di loro.</li><li>Non diamo consigli medici: per qualsiasi scelta sul farmaco, chiedi al medico o al farmacista.</li>'
             '<li>Non raccogliamo dati di chi legge, a parte il modulo facoltativo per segnalare un errore.</li></ul></div>'
             '<h2>Come si sostiene</h2><div class="testo"><p>Il sito può mostrare pubblicità di Google AdSense nelle pagine con più contenuto. La pubblicità non cambia '
             'nessun dato e nessuno paga per comparire. Non ci sono link di affiliazione a farmaci.</p><p>Farmaco Equivalente fa parte di una piccola rete di siti '
             'informativi gratuiti dello stesso gestore. Come controlliamo i dati: <a href="/come-lavoriamo/">come lavoriamo</a>.</p></div>')
    testata = banda("Chi siamo", "Chi siamo", "Un sito indipendente che rende leggibili gli elenchi ufficiali AIFA.", corta=True, icona="info")
    pagina("chi-siamo/", "Chi siamo | Farmaco Equivalente",
           "Farmaco Equivalente è un sito indipendente e gratuito, non affiliato ad AIFA, con equivalenti, prezzi di riferimento e farmaci carenti.",
           corpo, testata, briciole=[("Home", ""), ("Chi siamo", "chi-siamo/")])


def privacy():
    cookie = MON.privacy_cookie("it", SITO_ID) or ('<h2>Cookie e contatore visite</h2><p>Per contare le visite usiamo GoatCounter, che non usa cookie. '
                                                  'Il sito non usa cookie di profilazione e non mostra pubblicità.</p>')
    corpo = ('<div class="card pull testo"><p>Questa pagina spiega quali dati tratta Farmaco Equivalente. In breve: pochissimi, e mai dati sulla salute.</p></div>'
             '<div class="testo"><h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce Farmaco Equivalente come progetto indipendente. '
             'Puoi scriverci con il modulo <a href="/come-lavoriamo/#segnala">«Segnala un errore»</a>, anche per le richieste sui tuoi dati.</p>'
             '<h2>La ricerca dei farmaci</h2><p>La ricerca nella home e il filtro dell\'elenco dei carenti funzionano nel tuo browser: i nomi che scrivi non vengono '
             'inviati né salvati. Il sito ricorda nel browser solo la scelta del tema chiaro o scuro (memoria locale).</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>Il sito è ospitato da Netlify, Inc., che tratta dati tecnici (come l\'indirizzo IP) per consegnare le pagine e proteggere il servizio. '
             'Netlify può trattare i dati fuori dall\'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>'
             '<h2 id="segnalazioni">Modulo «Segnala un errore»</h2><p>Se usi il modulo riceviamo la pagina che indichi, il messaggio, il link alla fonte e, solo se la scrivi, '
             'la tua email. Ti chiediamo di non scrivere dati sulla tua salute. Il modulo è gestito da Netlify Forms per nostro conto. Usiamo questi dati solo per '
             'controllare la segnalazione e, se hai lasciato l\'email, risponderti; li cancelliamo quando la segnalazione è chiusa. La base giuridica è il consenso '
             'dato con la casella del modulo (art. 6.1.a GDPR), che puoi ritirare quando vuoi: per chiedere la cancellazione basta un\'altra segnalazione. '
             'Non ci sono account né newsletter.</p>'
             '<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e fare reclamo al Garante per la protezione dei dati '
             'personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>'
             f'<h2>Modifiche</h2><p>Aggiorniamo questa pagina quando il sito cambia. Ultimo aggiornamento: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("it", SITO_ID) or "Cosa raccogliamo (pochissimo) e come funziona il contatore delle visite."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", "Privacy | Farmaco Equivalente",
           "Privacy di Farmaco Equivalente: ricerca nel browser, nessun dato sulla salute, contatore delle visite senza cookie e pubblicità solo con il tuo consenso.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = ('<div class="card pull"><p>La pagina che cerchi non esiste. Torna alla <a href="/">ricerca dei farmaci</a>, all\'<a href="/#indice">elenco dei '
             'principi attivi</a> o all\'<a href="/carenze/">elenco dei farmaci carenti</a>.</p></div>')
    testata = banda("Errore 404", "Pagina non trovata", "Questo indirizzo non ha una pagina.", corta=True, icona="alert")
    pagina("", "Pagina non trovata | Farmaco Equivalente", "Pagina non trovata.", corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{CONTROLLO.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in farmaci/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = farmaci/sito, Build command vuoto, Publish directory = "."
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


def controlli():
    err = []
    for pid, p in FJ["pagine"].items():
        if p.get("http") != 200:
            err.append(f"pagina {pid}: HTTP {p.get('http')}")
        manca = [c[:60] for c, ok in p["trovate"].items() if not ok]
        if manca:
            err.append(f"pagina {pid}: frasi non trovate {manca}")
    for fid, f in FJ["file"].items():
        if f.get("http") != 200 or not f.get("pubblicato_il"):
            err.append(f"file {fid}: HTTP {f.get('http')} o data di pubblicazione mancante")
    if CA.get("aggiornato_al_nel_file") != CA["pubblicato_il"]:
        err.append(f"carenti: data nel file {CA.get('aggiornato_al_nel_file')} diversa da quella della pagina AIFA {CA['pubblicato_il']}")
    for g, rr in GRUPPI.items():
        if len({r["rif"] for r in rr}) != 1:
            err.append(f"gruppo {g}: più prezzi di riferimento")
        if len({r["pa"] for r in rr}) != 1:
            err.append(f"gruppo {g}: più principi attivi")
    non_letti = [p for p in PA if not LETTI[p]]
    if non_letti:
        print(f"AVVISO: {len(non_letti)} principi attivi con nomi non ancora cercati in domanda.json (pagina noindex se non c'è altra prova)", file=sys.stderr)
    if (date.today() - DATA_C).days > 10:
        print(f"AVVISO: elenco carenti del {DATA_C}: più di 10 giorni, rilanciare raccolta/fonti.py --rete", file=sys.stderr)
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err))


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
    carenze()
    farmaco_mancante()
    faq_tot = 0
    faq_usate = []
    for p in sorted(PA):
        v = pagina_pa(p)
        if INDICIZZA[p]:
            faq_tot += len(v)
        faq_usate += [{"pagina": SLUG[p], "q": q, "ricerca": s, "indicizzata": INDICIZZA[p]} for q, _, _, s in v]
    n_idx = sum(INDICIZZA.values())
    come_lavoriamo(n_idx, len(PA) - n_idx, faq_tot + sum(1 for x in FAQ))
    chi_siamo()
    privacy()
    pagina_404()
    extra()
    (DATI / "faq_pagine.json").write_text(json.dumps({"_nota": "FAQ costruite da genera.py dalle ricerche salvate (solo lettura: verifica.py le confronta)",
                                                       "faq": faq_usate}, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili (di cui {n_idx} principi attivi) + {len(PA) - n_idx} principi attivi noindex + 404. "
          f"Lista di trasparenza del {DATA_T}, carenti del {DATA_C}.")


if __name__ == "__main__":
    main()
