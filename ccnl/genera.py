"""Genera il sito statico "Paga CCNL" (italiano) in ccnl/sito/: minimi contrattuali e paga oraria per contratto e livello.

Uso (dalla radice del repository):
    python3 ccnl/raccolta/fonti.py      # scarica le fonti ufficiali -> raccolta/_grezzi/, dati/fonti.json, dati/cnel_monitor.json
    python3 ccnl/raccolta/estrai.py     # estrae e incrocia le cifre -> dati/estratti.json, dati/contratti.json
    python3 ccnl/raccolta/domanda.py    # ricerche vere (autocompletamento) -> dati/domanda.json
    python3 ccnl/genera.py              # pagine in ccnl/sito/
    python3 ccnl/verifica.py            # controlli (--browser per Playwright)

Si pubblicano solo le cifre "pubblicabili" di dati/contratti.json: somma delle parti uguale al totale stampato e seconda
fonte uguale al centesimo. Tutti gli importi sono lordi e minimi. Niente netto, niente consigli. Nessun dato personale.
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from html import escape, unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import stile  # noqa: E402

URL_SITO = "https://paga-ccnl.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
NOME = "Paga CCNL"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "ccnl"  # nome del sito in monetizzazione.json
MIN_PAROLE_ADSENSE = 400  # come EsameB1: niente pubblicità nelle pagine noindex o con poco testo


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


META = carica("contratti_meta.json")
C = META["contratti"]
RIS = carica("contratti.json")["contratti"]
EST = carica("estratti.json")
_F = carica("fonti.json")
FONTI_DEF, FONTI = _F["definizioni"], _F["fonti"]
PAGINE_UFF = _F["pagine"]
FAQ = carica("faq.json")["faq"]
DOMANDA = carica("domanda.json")
CONTROLLO = date.fromisoformat(META["controllato_il"])
OGGI = date.today()
ORDINE = ["terziario", "metalmeccanici", "multiservizi", "logistica", "domestico"]

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    g = "1°" if d.day == 1 else str(d.day)
    return f"{g} {MESI[d.month - 1]} {d.year}"


def D(x):
    return Decimal(str(x))


def arr(x):
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def euro(x, simbolo=True):
    x = arr(x)
    s = f"{abs(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if x < 0 else "") + s + (" €" if simbolo else "")


def cent(x):
    return int(arr(x) * 100)


def da_cent(n):
    return Decimal(n) / 100


def prorata(mensile, ore, ore_norm):
    """Mensile per un orario ridotto, arrotondato al centesimo con il mezzo verso l'alto (interi, come in APP_JS)."""
    c = cent(mensile)
    return da_cent((2 * c * ore + ore_norm) // (2 * ore_norm))


def orario52(oraria, ore):
    """Lavoro domestico a ore: paga oraria × ore settimanali × 52 ÷ 12 (chiarimento a verbale n. 1)."""
    c = cent(oraria)
    return da_cent((2 * c * ore * 52 + 12) // 24)


def div(x, n):
    return arr(D(x) / D(n))


# ---------------------------------------------------------------- dati per livello
def tranche_livello(cid, lid):
    for L in RIS[cid]["livelli"]:
        if L["id"] == lid:
            return L["tranche"]
    raise KeyError((cid, lid))


def stato_livello(cid, L):
    """(tranche in vigore oggi, tranche passate pubblicabili, tranche future, tranche escluse)."""
    tr = tranche_livello(cid, L["id"])
    passate = [t for t in tr if t["dal"] <= OGGI.isoformat()]
    cur = passate[-1] if passate else None
    future = [t for t in tr if t["dal"] > OGGI.isoformat()]
    return cur, [t for t in passate[:-1] if t["pubblicabile"]], future


def livelli_pubblicati(cid):
    out = []
    for L in C[cid]["livelli"]:
        cur, _, _ = stato_livello(cid, L)
        if cur and cur["pubblicabile"]:
            out.append(L)
    return out


def totale(t):
    if t.get("totale"):
        return D(t["totale"])
    return D(t["parti"][0][1])  # domestico: minimo mensile del convivente


def valori(cid, L):
    """Tutte le cifre di una pagina livello, calcolate qui una volta sola (verifica.py le ricalcola)."""
    m = C[cid]
    cur, storico, future = stato_livello(cid, L)
    v = {"cur": cur, "storico": storico, "future": future, "dal": cur["dal"]}
    if cid == "domestico":
        tab = cur["tabelle"]
        v["oraria"] = D(tab["C_oraria"])
        v["conv"] = D(tab["A_mensile"])
        v["ind"] = D(tab["A_indennita"]) if tab.get("A_indennita") else None
        v["mensile"] = v["conv"]
        v["conv_tot"] = v["conv"] + (v["ind"] or 0)
        v["annuo_conv"] = v["conv_tot"] * 13
        v["tab"] = tab
        v["ore_norm"] = 40
        v["p"] = {o: orario52(v["oraria"], o) for o in (10, 20, 25, 30, 40)}
        v["giornaliera_conv"] = div(v["conv_tot"], 26)
        return v
    v["mensile"] = totale(cur)
    v["ore_norm"] = m["ore"]["valore"]
    v["oraria"] = div(v["mensile"], m["divisore_orario"]["valore"])
    v["giornaliera"] = div(v["mensile"], m["divisore_giornaliero"]["valore"]) if m.get("divisore_giornaliero") else None
    if m.get("divisore_giornaliero") and m["divisore_giornaliero"].get("valore_alt"):
        v["giornaliera_alt"] = div(v["mensile"], m["divisore_giornaliero"]["valore_alt"])
    v["annuo"] = v["mensile"] * m["mensilita"]["valore"]
    v["p"] = {o: prorata(v["mensile"], o, v["ore_norm"]) for o in sorted({20, 24, 30, v["ore_norm"]})}
    fut_ok = [t for t in future if t["pubblicabile"]]
    v["prossima"] = fut_ok[0] if fut_ok else None
    return v


def pagina_url(cid, L=None):
    return f"{C[cid]['slug']}/" + (f"{L['slug']}/" if L else "")


# ---------------------------------------------------------------- segnaposto delle FAQ
def segnaposto(testo):
    def sost(mm):
        cid, lid, campo = mm.group(1), mm.group(2), mm.group(3)
        if cid == "domestico" and lid == "unico":
            if campo == "e":
                return euro(EST["domestico"]["A"]["unico"]["E_mensile"])
            raise KeyError(campo)
        L = next(x for x in C[cid]["livelli"] if x["id"] == lid)
        v = valori(cid, L)
        if campo in ("mensile", "oraria", "giornaliera", "annuo", "conv", "ind", "annuo_conv"):
            return euro(v[campo])
        if campo == "dal":
            return data_lunga(v["dal"])
        if re.fullmatch(r"p\d+", campo):
            return euro(v["p"][int(campo[1:])])
        if campo == "prossimo_mensile":
            return euro(totale(v["prossima"]))
        if campo == "prossimo_dal":
            return data_lunga(v["prossima"]["dal"])
        if campo == "tab_b":
            return euro(v["tab"]["B_mensile"])
        if campo == "d_auto":
            return euro(v["tab"]["D_autosuff"])
        if campo == "d_non":
            return euro(v["tab"]["D_non_autosuff"])
        raise KeyError(campo)
    return re.sub(r"\{([a-z]+)/([a-z0-9_]+):([a-z0-9_]+)\}", sost, testo)


# ---------------------------------------------------------------- fonti numerate
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
        if not nums:
            return ""
        return '<sup class="ref">' + ",".join(f'<a href="#f{n}" aria-label="fonte {n}">[{n}]</a>' for n in sorted(set(nums))) + "</sup>"

    def elenco(self):
        if not self.ordine:
            return ""
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f, es = FONTI_DEF[i], FONTI[i]
            voci.append(f'<li id="f{n}"><a href="{h(es["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. '
                        f'<span class="small">Letto il {data_lunga(es["letto_il"])}.</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Fonti</h2><ol>{"".join(voci)}</ol>'
                f'<p class="small">Controllato il {data_lunga(CONTROLLO)}. Come leggiamo e confrontiamo le fonti: <a href="/come-lavoriamo/">come lavoriamo</a>.</p></section>')


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
MENU = [("terziario-commercio/", "Commercio"), ("metalmeccanici-industria/", "Metalmeccanici"), ("multiservizi-pulizie/", "Multiservizi"),
        ("logistica-trasporto-merci/", "Logistica"), ("colf-badanti/", "Colf e badanti"), ("come-lavoriamo/", "Come lavoriamo")]
DISCLAIMER = ("<strong>Importi lordi minimi del contratto nazionale.</strong> Non comprendono scatti di anzianità, superminimi, premi, indennità "
              "aziendali, straordinari e contratti integrativi, e sono prima di contributi e tasse: il netto non lo calcoliamo. Sono informazioni "
              "generali, non consulenza: per il tuo caso chiedi a un consulente del lavoro, al sindacato o a un patronato.")


def parole_principali(corpo):
    t = re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    return len(re.findall(r"\w+", t))


def menu_html(percorso):
    return "".join(f'<a href="/{u}"' + (' aria-current="page"' if percorso.startswith(u) else "") + f">{h(t)}</a>" for u, t in MENU)


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
    contratti_piede = "".join(f'<li><a href="/{C[c]["slug"]}/">{h(C[c]["nome_breve"])}</a></li>' for c in ORDINE)
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
<meta name="theme-color" content="#14233A">
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
<a class="logo" href="/">{LOGO}<span>Paga <b>CCNL</b></span></a>
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
<a class="logo" href="/">{LOGO}<span>Paga <b>CCNL</b></span></a>
<p><strong>{NOME}</strong> riporta i minimi dei contratti collettivi nazionali per livello, con la paga oraria calcolata con il divisore scritto
nel contratto. Ogni cifra viene da due fonti ufficiali confrontate al centesimo. È un sito indipendente: non è del CNEL, del Ministero del Lavoro,
di un sindacato o di un'associazione di imprese.</p>
<p>Fonti controllate il {data_lunga(CONTROLLO)}.</p>
</div><div>
<h2>Contratti</h2><ul>{contratti_piede}<li><a href="/colf-badanti/">Colf e badanti: guida per le famiglie</a></li></ul>
</div><div>
<h2>Il sito</h2><ul><li><a href="/come-lavoriamo/">Come lavoriamo</a></li><li><a href="/come-lavoriamo/#segnala">Segnala un errore</a></li>
<li><a href="/chi-siamo/">Chi siamo</a></li><li><a href="/privacy/">Privacy</a></li></ul>
</div></div>
<p class="f-base">Importi lordi minimi, senza scatti, superminimi e integrativi. Informazioni generali, non consulenza del lavoro. I testi ufficiali
dei contratti sono nell'<a href="https://www.cnel.it/Archivio-Contratti" rel="noopener">archivio del CNEL</a>.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="euro"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def faq_blocco(pid, rim, titolo="Domande frequenti"):
    voci = [x for x in FAQ if x["pagina"] == pid]
    if not voci:
        return "", None
    blocchi, ld = [], []
    for x in voci:
        a = segnaposto(x["a"])
        blocchi.append(f'<div class="faq"><h3>{h(x["q"])}</h3><p>{h(a)}{rim.ref(x["fonti"])}</p></div>')
        ld.append({"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": a}})
    html_ = f'<h2 id="faq">{h(titolo)}</h2><p class="small">Domande che le persone cercano davvero su Google, con la risposta presa dalle fonti.</p>' + "".join(blocchi)
    return html_, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


def calcolatore(v, modo, mensilita, titolo, etichetta, max_ore, nota):
    """Riquadro del calcolo per ore settimanali (solo lordo). modo: prorata | orario52."""
    base = v["oraria"] if modo == "orario52" else v["mensile"]
    ore_def = 20 if modo == "orario52" else (30 if v["ore_norm"] >= 30 else v["ore_norm"])
    chips = [10, 20, 25, 30, 40] if modo == "orario52" else sorted({20, 24, 30, v["ore_norm"]})
    out = orario52(base, ore_def) if modo == "orario52" else prorata(base, ore_def, v["ore_norm"])
    return f"""<section class="card calc" data-calc data-modo="{modo}" data-cent="{cent(base)}" data-ore-normali="{v['ore_norm']}" data-mensilita="{mensilita}" aria-labelledby="calc-h">
<div class="calc-h"><h2 id="calc-h">{ico("calc")}{h(titolo)}</h2><span class="pill">Lordo</span></div>
<div class="calc-g"><div class="calc-in">
<label>{h(etichetta)}<input name="ore" type="number" inputmode="numeric" min="1" max="{max_ore}" step="1" value="{ore_def}"></label>
<div class="chips" role="group" aria-label="Ore settimanali">{"".join(f'<button type="button" data-ore="{o}" aria-pressed="{str(o == ore_def).lower()}">{o} ore</button>' for o in chips)}</div>
</div><div class="calc-out" aria-live="polite">
<div class="esito"><span>Minimo lordo al mese</span><b data-out>{euro(out)}</b></div>
<div class="esito sec"><span>Lordo in un anno ({mensilita} mensilità)</span><b data-out-annuo>{euro(out * mensilita)}</b></div>
</div></div>
<p class="calc-f">{nota}</p>
</section>"""


def tabella(intest, righe, caption="", num=None, classi=None):
    num = num if num is not None else list(range(1, len(intest)))
    th = "".join(f'<th scope="col"{" class=\"n\"" if i in num else ""}>{x}</th>' for i, x in enumerate(intest))
    body = ""
    for k, r in enumerate(righe):
        cl = f' class="{classi[k]}"' if classi and classi[k] else ""
        body += f"<tr{cl}>" + "".join(f'<td{" class=\"n\"" if i in num else ""}>{x}</td>' for i, x in enumerate(r)) + "</tr>"
    cap = f"<caption>{caption}</caption>" if caption else ""
    return f'<div class="tab"><table class="dati">{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def nota(testo, tipo="info", icona="info"):
    return f'<div class="nota {tipo}">{ico(icona)}<p>{testo}</p></div>'


def nome_corto(L):
    return re.sub(r"\s*\(.*?\)", "", L["nome"]).replace(", ", " ")


def titolo_livello(cid, L):
    m = C[cid]
    anno = date.fromisoformat(valori(cid, L)["dal"]).year
    if cid == "domestico":
        nl = L["nome"][0].lower() + L["nome"][1:]
        cands = [f"{m['nome_titolo']} {nl}: paga oraria e stipendio {anno}", f"{m['nome_titolo']} {nl}: paga e stipendio {anno}"]
    else:
        cands = [f"{L['nome']} {m['nome_titolo']}: paga oraria e minimo {anno}", f"{nome_corto(L)} {m['nome_titolo']}: paga oraria e minimo {anno}",
                 f"{nome_corto(L)} {m['nome_titolo']}: minimo {anno}"]
    for t in cands:
        if len(t) <= 65:
            return t
    raise SystemExit(f"titolo troppo lungo: {cands[-1]}")


def descr_livello(cid, L, v):
    m = C[cid]
    if cid == "domestico":
        cands = [f"{L['nome']} del lavoro domestico nel 2026: {euro(v['oraria'])} l'ora non convivente, {euro(v['conv'])} al mese convivente. Calcolo per ore e fonti ufficiali.",
                 f"{L['nome']} colf e badanti 2026: {euro(v['oraria'])} l'ora, {euro(v['conv'])} al mese da convivente. Calcolo per ore e fonti."]
    else:
        cands = [f"{L['nome']} del CCNL {m['nome_breve'].lower()}: minimo {euro(v['mensile'])} dal {data_lunga(v['dal'])}, {euro(v['oraria'])} l'ora (divisore {m['divisore_orario']['valore']}), part time e aumenti.",
                 f"{nome_corto(L)} CCNL {m['nome_breve'].lower()}: {euro(v['mensile'])} al mese dal {data_lunga(v['dal'])}, {euro(v['oraria'])} l'ora, part time e aumenti.",
                 f"{nome_corto(L)} {m['nome_titolo']}: {euro(v['mensile'])} al mese, {euro(v['oraria'])} l'ora, part time e aumenti."]
    for t in cands:
        if 70 <= len(t) <= 160:
            return t
    raise SystemExit(f"descrizione fuori misura: {cands}")


# ---------------------------------------------------------------- pagina livello (contratti con divisore)
def vicini(cid, L):
    pub = livelli_pubblicati(cid)
    i = pub.index(L)
    gruppo = L.get("gruppo_nome")
    pre = [x for x in pub[:i] if x.get("gruppo_nome") == gruppo]
    dopo = [x for x in pub[i + 1:] if x.get("gruppo_nome") == gruppo]
    return (pre[-1] if pre else None), (dopo[0] if dopo else None)


def pagina_livello(cid, L):
    m = C[cid]
    v = valori(cid, L)
    rim = Rimandi()
    fa, fb = m["fonte_a"], m["fonte_b"]
    cur = v["cur"]
    div_o, div_g = m["divisore_orario"], m.get("divisore_giornaliero")
    mens = m["mensilita"]["valore"]
    # cifre in alto
    cifre = (f'<div class="card cifre pull">'
             f'<div class="cifra main"><b>{euro(v["mensile"])}</b><span>minimo lordo al mese, dal {data_lunga(v["dal"])}</span></div>'
             f'<div class="cifra"><b>{euro(v["oraria"])}</b><span>paga oraria lorda (÷ {div_o["valore"]})</span></div>'
             + (f'<div class="cifra"><b>{euro(v["giornaliera"])}</b><span>paga giornaliera (÷ {div_g["valore"]})</span></div>' if v.get("giornaliera") else
                f'<div class="cifra"><b>{m["ore"]["valore"]} ore</b><span>orario settimanale del contratto</span></div>')
             + f'<div class="cifra"><b>{euro(v["annuo"])}</b><span>minimo lordo annuo ({mens} mensilità)</span></div>'
             f'<p class="asof">{ico("check")} Stessa cifra in due fonti ufficiali{rim.ref([fa, fb])}. Controllato il {data_lunga(CONTROLLO)}.</p></div>')
    corpo = cifre
    # voci
    righe = [(h(n), euro(x)) for n, x in cur["parti"]]
    corpo += f'<h2 id="voci">Le voci del minimo mensile</h2>'
    corpo += (f'<p>Il minimo del {h(L["nome"])} {h(articolo_contratto(cid))} è la somma delle voci stampate nella tabella del contratto. '
              f'In vigore dal {data_lunga(v["dal"])}.{rim.ref(fa)}</p>')
    t = tabella(["Voce", "Importo mensile"], righe + [("<strong>Totale</strong>", f"<strong>{euro(v['mensile'])}</strong>")])
    corpo += t + verifica_frase(cid, L, cur, rim)
    if cid == "terziario":
        corpo += f'<p class="small">{h(m["terzo_elemento"]["testo"])}{rim.ref(fa)}</p>'
    if cid == "multiservizi" and cur.get("edr"):
        corpo += (f'<p class="small">Le tabelle dell\'accordo stampano a parte anche l\'E.D.R. di {euro(cur["edr"])} al mese (elemento distinto della retribuzione), '
                  f'che qui non è sommato al minimo.{rim.ref(fb)}</p>')
    if cid == "metalmeccanici":
        corpo += ('<p class="small">Nel minimo tabellare è già compresa l\'ex indennità di contingenza (art. 5). Non sono compresi gli scatti biennali, '
                  f'l\'elemento perequativo e i 250 euro l\'anno di strumenti di welfare previsti dal rinnovo.{rim.ref(["cnel_157071", "fm_accordo_2025"])}</p>')
    # paga oraria e giornaliera
    corpo += '<h2 id="oraria">Paga oraria e giornaliera</h2>'
    corpo += (f'<div class="formula">{euro(v["mensile"])} ÷ {div_o["valore"]} = <strong>{euro(v["oraria"])}</strong> l\'ora'
              f'<small>Divisore orario {div_o["valore"]}: {h(div_o["dove"])}{rim.ref(div_o["fonte"])}'
              + (f'. Per chi ha un orario normale diverso il contratto usa {h(div_o["altri"])}.' if div_o.get("altri") else ".") + "</small></div>")
    if v.get("giornaliera"):
        extra5 = (f' Con il divisore {div_g["valore_alt"]}: {euro(v["mensile"])} ÷ {div_g["valore_alt"]} = {euro(v["giornaliera_alt"])}.' if v.get("giornaliera_alt") else "")
        corpo += (f'<div class="formula">{euro(v["mensile"])} ÷ {div_g["valore"]} = <strong>{euro(v["giornaliera"])}</strong> al giorno'
                  f'<small>{h(div_g.get("nota") or "Divisore giornaliero " + str(div_g["valore"]))}: {h(div_g["dove"])}{rim.ref(div_g["fonte"])}.{extra5}</small></div>')
    else:
        corpo += f'<p>{h(m["nota_giornaliera"])}{rim.ref(div_o["fonte"])}</p>'
    corpo += (f'<p>La paga oraria è quella del contratto, non quella effettiva: serve per calcolare ore di permesso, straordinari e trattenute. '
              f'Il contratto prevede {h(m["ore"]["testo"])} ({h(m["ore"]["dove"])}).{rim.ref(m["ore"]["fonte"])}</p>')
    # calcolatore
    corpo += calcolatore(v, "prorata", mens, "Part time: il minimo per le tue ore", "Ore settimanali", v["ore_norm"],
                         f"Proporzione sull'orario del contratto ({v['ore_norm']} ore): minimo × ore ÷ {v['ore_norm']}. Lordo, senza scatti e altre voci. "
                         "Il calcolo avviene nel tuo browser: non inviamo niente.")
    corpo += AD
    righe_p = [(f"{o} ore" + (" (tempo pieno)" if o == v["ore_norm"] else ""), euro(x), euro(x * mens)) for o, x in v["p"].items()]
    corpo += '<h2 id="part-time">Il minimo a 20, 24, 30 ore e a tempo pieno</h2>'
    corpo += (f'<p>Nel part time la paga si riproporziona sulle ore: per il {h(L["nome"])} la paga oraria resta {euro(v["oraria"])}, '
              f'il mensile cambia con l\'orario.</p>')
    corpo += tabella(["Ore settimanali", "Minimo al mese", f"In un anno ({mens} mensilità)"], righe_p)
    # annuo
    corpo += '<h2 id="annuo">Minimo lordo annuo</h2>'
    corpo += (f'<div class="formula">{euro(v["mensile"])} × {mens} = <strong>{euro(v["annuo"])}</strong>'
              f'<small>{mens} mensilità: {h(m["mensilita"]["dove"])}{rim.ref(m["mensilita"]["fonte"])}</small></div>')
    corpo += (f'<p>È il minimo annuo a tempo pieno con la tabella in vigore oggi. Se nell\'anno arriva un aumento, il totale dell\'anno sarà più alto.</p>')
    # aumenti futuri e storico
    corpo += aumenti_html(cid, L, v, rim)
    # vicini
    pre, dopo = vicini(cid, L)
    if pre or dopo:
        rr, cl = [], []
        for x, qui in [(pre, False), (L, True), (dopo, False)]:
            if not x:
                continue
            vx = valori(cid, x)
            nome = h(x["nome"]) if qui else f'<a href="/{pagina_url(cid, x)}">{h(x["nome"])}</a>'
            diff = "" if qui else (("+" if vx["mensile"] > v["mensile"] else "") + euro(vx["mensile"] - v["mensile"]))
            rr.append((nome, euro(vx["mensile"]), euro(vx["oraria"]), diff))
            cl.append("qui" if qui else "")
        corpo += '<h2 id="vicini">Confronto con i livelli vicini</h2>'
        corpo += tabella(["Livello", "Minimo al mese", "Paga oraria", "Differenza al mese"], rr, classi=cl)
    # declaratoria
    dec = L.get("declaratoria")
    if dec:
        corpo += f'<h2 id="chi">Chi è inquadrato a questo livello</h2>'
        corpo += f'<p>Il contratto ({h(dec["dove"])}) descrive così il livello: «{h(pulisci_citazione(dec["testo"]))}…»{rim.ref(dec["fonte"])}</p>'
        if dec.get("profili"):
            corpo += f'<p>Profili indicati come esempio: {h("; ".join(dec["profili"]))}.</p>'
        corpo += '<p class="small">Il livello si decide in base alle mansioni svolte davvero, non al titolo scritto nel contratto individuale.</p>'
    # cosa non comprende
    corpo += ('<h2 id="non-compreso">Cosa non c\'è in queste cifre</h2><div class="testo"><ul>'
              '<li>scatti di anzianità, superminimi e aumenti di merito;</li><li>straordinari, maggiorazioni, indennità di turno o di trasferta;</li>'
              '<li>premi e importi dei contratti aziendali o territoriali;</li><li>contributi e tasse: sono cifre lorde, il netto in busta paga è più basso.</li></ul></div>')
    faq_html, faq_ld = faq_blocco(f"{cid}/{L['id']}", rim)
    corpo += faq_html
    corpo += f'<h2 id="altri">Gli altri livelli del contratto</h2>' + lista_livelli(cid, L)
    corpo += documento_ufficiale(cid, rim)
    corpo += rim.elenco()
    titolo = titolo_livello(cid, L)
    sub = (f'Minimo in vigore dal <strong>{data_lunga(v["dal"])}</strong>: {euro(v["mensile"])} lordi al mese, {euro(v["oraria"])} l\'ora. '
           f'{h(m["nome"])}, codice CNEL {m["codice_cnel"]}.')
    testata = banda(m["nome_breve"], titolo.split(":")[0], sub)
    ld = [x for x in [faq_ld] if x]
    pagina(pagina_url(cid, L), titolo, descr_livello(cid, L, v), corpo, testata,
           briciole=[("Home", ""), (m["nome_breve"], pagina_url(cid)), (L["nome"], pagina_url(cid, L))], jsonld=ld)


def articolo_contratto(cid):
    return {"terziario": "nel CCNL terziario", "metalmeccanici": "nel CCNL metalmeccanici", "multiservizi": "nel CCNL multiservizi",
            "logistica": "nel CCNL logistica"}[cid]


def pulisci_citazione(t):
    return re.sub(r"(\w)- (\w)", r"\1\2", t).replace("ﬁ", "fi").replace("ﬂ", "fl")


def verifica_frase(cid, L, t, rim):
    fa, fb = C[cid]["fonte_a"], C[cid]["fonte_b"]
    b = t["fonte_b"]
    if cid == "terziario":
        s = (f'Controllo: la somma delle voci è uguale al totale stampato ({euro(t["totale"])}) e la tabella di Filcams CGIL riporta la stessa paga base '
             f'({euro(b["paga_base"])}) e la stessa contingenza ({euro(b["contingenza"])}). Il totale di Filcams è {euro(b["totale"])} perché comprende anche il terzo elemento nazionale.')
    elif cid == "metalmeccanici":
        s = (f'Controllo: il Ministero stampa la retribuzione tabellare annua ({euro(t["fonte_a"]["annuo"])}), che divisa per 12 dà {euro(t["fonte_a"]["mensile"])}; '
             f'l\'accordo di rinnovo del 22 novembre 2025 stampa lo stesso minimo dal 1° giugno 2026.')
    elif cid == "multiservizi":
        s = (f'Controllo: il Ministero stampa gli importi annui (tabellare {euro(t["fonte_a"]["annuo_tabellare"])}, contingenza {euro(t["fonte_a"]["annuo_contingenza"])}), '
             f'che divisi per 12 danno le cifre qui sopra; l\'accordo del 6 agosto 2025 stampa le stesse voci e la stessa retribuzione base ({euro(b["base"])}).')
    elif cid == "logistica":
        s = (f'Controllo: minimo ed EPA sommano al totale stampato nel contratto ({euro(t["totale"])}); il Ministero stampa gli importi annui '
             f'(retribuzione base {euro(b["annuo_base"])}, EPA {euro(b["annuo_epa"])}), che divisi per 12 danno le stesse cifre.')
    return f'<p class="small">{ico("check")} {h(s)}{rim.ref([fa, fb])}</p>'


def aumenti_html(cid, L, v, rim):
    m = C[cid]
    fa, fb = m["fonte_a"], m["fonte_b"]
    out = '<h2 id="aumenti">Aumenti già firmati</h2>'
    fut = v["future"]
    pub = [t for t in fut if t["pubblicabile"]]
    if pub:
        righe, prec = [], v["mensile"]
        for t in pub:
            tot = totale(t)
            righe.append((data_lunga(t["dal"]), euro(tot), "+" + euro(tot - prec), euro(div(tot, m["divisore_orario"]["valore"]))))
            prec = tot
        out += f'<p>Il contratto fissa già i prossimi minimi del {h(L["nome"])}.{rim.ref([fa, fb])}</p>'
        out += tabella(["Dal", "Minimo al mese", "Aumento", "Paga oraria"], righe)
    escl = [t for t in fut if not t["pubblicabile"]]
    for t in escl:
        if cid == "metalmeccanici":
            continue
        out += nota(f'Dal {data_lunga(t["dal"])} cambia di nuovo il minimo, ma la riga del contratto non passa i nostri controlli '
                    f'({h("; ".join(t["motivi"]))}): la pubblichiamo quando una fonte ufficiale la chiarisce.', "", "alert")
    if m.get("aumenti_futuri"):
        out += f'<p>{h(m["aumenti_futuri"]["testo"])}{rim.ref(m["aumenti_futuri"]["fonte"])}</p>'
    if not pub and not m.get("aumenti_futuri"):
        out += f'<p>Nessun altro aumento è scritto nel contratto fino alla scadenza ({data_lunga(m["testo"]["scadenza"])}).</p>'
    out += f'<p class="small">Il contratto scade il {data_lunga(m["testo"]["scadenza"])}; gli aumenti dopo quella data dipendono dal rinnovo.</p>'
    if v["storico"]:
        righe = [(data_lunga(t["dal"]), euro(totale(t)), euro(div(totale(t), m["divisore_orario"]["valore"]))) for t in v["storico"]] + \
                [(data_lunga(v["dal"]) + " (in vigore)", euro(v["mensile"]), euro(v["oraria"]))]
        out += f'<h3>I minimi precedenti</h3>' + tabella(["Dal", "Minimo al mese", "Paga oraria"], righe)
    return out


def lista_livelli(cid, L=None):
    return '<ul class="livelli">' + "".join(
        f'<li><a href="/{pagina_url(cid, x)}"' + (' aria-current="page"' if L and x["id"] == L["id"] else "") + f'>{h(x["nome"])}</a></li>'
        for x in livelli_pubblicati(cid)) + "</ul>"


def documento_ufficiale(cid, rim):
    m = C[cid]
    fonti = [m["testo"]["fonte"], m["fonte_a"], m["fonte_b"]]
    voci = []
    for f in dict.fromkeys(fonti):
        voci.append(f'<li><a href="{h(FONTI[f]["url"])}" rel="noopener">{h(FONTI_DEF[f]["titolo"])}</a> ({h(FONTI_DEF[f]["chi"])})</li>')
    return f'<h2 id="documenti">I documenti ufficiali</h2><div class="testo"><ul>{"".join(voci)}</ul></div>'


# ---------------------------------------------------------------- pagina livello del lavoro domestico
def pagina_domestico(L):
    cid, m = "domestico", C["domestico"]
    v = valori(cid, L)
    tab = v["tab"]
    rim = Rimandi()
    fa, fb = m["fonte_a"], m["fonte_b"]
    ind = v["ind"]
    cifre = (f'<div class="card cifre pull">'
             f'<div class="cifra main"><b>{euro(v["oraria"])}</b><span>paga oraria lorda, chi non convive (tabella C)</span></div>'
             f'<div class="cifra"><b>{euro(v["conv"])}</b><span>minimo mensile, chi convive (tabella A)</span></div>'
             + (f'<div class="cifra"><b>{euro(ind)}</b><span>indennità di funzione al mese (livelli D e DS)</span></div>' if ind else
                f'<div class="cifra"><b>{euro(v["p"][20])}</b><span>al mese a 20 ore settimanali, chi non convive</span></div>')
             + f'<div class="cifra"><b>{euro(v["annuo_conv"])}</b><span>minimo annuo da convivente (13 mensilità)</span></div>'
             f'<p class="asof">{ico("check")} Tabella in vigore dal {data_lunga(v["dal"])}, uguale nelle due copie ufficiali{rim.ref([fa, fb])}. Controllato il {data_lunga(CONTROLLO)}.</p></div>')
    corpo = cifre
    corpo += '<h2 id="tabelle">Le cifre del 2026 per questo livello</h2>'
    corpo += f'<p>Tutte le voci della tabella ufficiale per il {h(L["nome"][0].lower() + L["nome"][1:])}, decorrenza {data_lunga(v["dal"])} (aggiornamento ISTAT dell\'1,00% e prima rata di aumento del contratto).{rim.ref(fa)}</p>'
    righe = [("Convivente: minimo mensile (tabella A, art. 14 c. 1 lett. a)", euro(tab["A_mensile"]))]
    if ind:
        righe.append(("Convivente: indennità di funzione mensile (tabella A, art. 34)", euro(ind)))
        righe.append(("Convivente: minimo più indennità", euro(v["conv_tot"])))
    if tab.get("B_mensile"):
        righe.append(("Convivente fino a 30 ore settimanali: mensile (tabella B, art. 14 c. 2)", euro(tab["B_mensile"])))
    righe.append(("Non convivente: paga oraria (tabella C, art. 14 c. 1 lett. b)", euro(tab["C_oraria"])))
    if tab.get("D_autosuff"):
        righe.append(("Assistenza notturna a persone autosufficienti: mensile (tabella D, art. 10)", euro(tab["D_autosuff"])))
    if tab.get("D_non_autosuff"):
        righe.append(("Assistenza notturna a persone non autosufficienti: mensile (tabella D, art. 10)", euro(tab["D_non_autosuff"])))
    if tab.get("G_oraria"):
        righe.append(("Sostituzione nei riposi del titolare: paga oraria (tabella G, art. 14 c. 9)", euro(tab["G_oraria"])))
    if tab.get("H_mensile"):
        righe.append(("Baby sitter con bambini sotto i 6 anni: indennità mensile (tabella H, art. 34 c. 3)", euro(tab["H_mensile"])))
        righe.append(("Stessa indennità per chi è in tabella B / all'ora", f'{euro(tab["H_mensile_tab_b"])} / {euro(tab["H_oraria"])}'))
    if tab.get("I_mensile"):
        righe.append(("Assistenza a più persone non autosufficienti: indennità mensile / oraria (tabella I, art. 34 c. 4)", f'{euro(tab["I_mensile"])} / {euro(tab["I_oraria"])}'))
    if tab.get("L_mensile"):
        righe.append(("Certificazione UNI 11766: indennità mensile (tabella L, art. 34 c. 7)", euro(tab["L_mensile"])))
    corpo += tabella(["Voce", "Importo"], righe)
    corpo += (f'<p class="small">{ico("check")} Controllo: la tabella pubblicata dal Ministero del Lavoro e quella depositata al CNEL con il verbale '
              f'dell\'11 febbraio 2026 hanno le stesse {sum(1 for x in tab.values() if x)} cifre per questo livello, al centesimo.{rim.ref([fa, fb])}</p>')
    # calcolo a ore
    corpo += '<h2 id="ore">Chi non convive: il mensile per le ore settimanali</h2>'
    corpo += (f'<div class="formula">{euro(v["oraria"])} × ore settimanali × 52 ÷ 12 = minimo al mese'
              f'<small>Il contratto calcola la paga mensile a ore così: «paga oraria per numero di ore lavorate nella settimana per 52:12» (chiarimenti a verbale, punto 1).{rim.ref("cnel_245143")}</small></div>')
    corpo += calcolatore(v, "orario52", 13, "Colf o badante a ore: il minimo al mese", "Ore a settimana (massimo 40)", 40,
                         "Lordo, senza contributi INPS, ferie, TFR e vitto. Tredicesima compresa nel totale annuo (13 mensilità, art. 39). "
                         "Il calcolo avviene nel tuo browser.")
    corpo += AD
    righe_p = [(f"{o} ore", euro(x), euro(x * 13)) for o, x in v["p"].items()]
    corpo += tabella(["Ore a settimana", "Minimo al mese", "In un anno (13 mensilità)"], righe_p)
    # convivente
    corpo += '<h2 id="convivente">Chi convive con la famiglia</h2>'
    corpo += (f'<p>Il minimo mensile di {euro(v["conv"])}' + (f' più l\'indennità di funzione di {euro(ind)}' if ind else "") +
              f' vale per un orario fino a 10 ore al giorno non consecutive e 54 ore a settimana ({h(m["ore"]["dove"])}).{rim.ref(m["ore"]["fonte"])} '
              f'Vitto e alloggio sono dovuti in natura: se non vengono dati, si pagano {euro(tab["F_totale"] if tab.get("F_totale") else EST["domestico"]["A"]["BS"]["F_totale"])} al giorno '
              f'(tabella F).{rim.ref(fa)}</p>')
    corpo += (f'<div class="formula">{euro(v["conv_tot"])} ÷ 26 = <strong>{euro(v["giornaliera_conv"])}</strong> al giorno'
              f'<small>Quota giornaliera: 1/26 della retribuzione mensile (chiarimenti a verbale, punto 1).{rim.ref("cnel_245143")}</small></div>')
    corpo += (f'<div class="formula">{euro(v["conv_tot"])} × 13 = <strong>{euro(v["annuo_conv"])}</strong> l\'anno'
              f'<small>Tredicesima: una mensilità in più a dicembre, che comprende anche il valore di vitto e alloggio (art. 39).{rim.ref("cnel_245143")}</small></div>')
    # aumenti
    corpo += '<h2 id="aumenti">Aumenti già firmati</h2>'
    corpo += f'<p>{h(m["aumenti_futuri"]["testo"])}{rim.ref(m["aumenti_futuri"]["fonte"])}</p>'
    corpo += f'<p class="small">Il contratto è in vigore dal {data_lunga(m["testo"]["decorrenza"])} al {data_lunga(m["testo"]["scadenza"])}. La tabella con le cifre del 2027 la pubblica il Ministero all\'inizio dell\'anno.</p>'
    # declaratoria
    dec = L["declaratoria"]
    corpo += '<h2 id="chi">Chi è inquadrato a questo livello</h2>'
    corpo += f'<p>Dal contratto ({h(dec["dove"])}): «{h(pulisci_citazione(dec["testo"]))}…»{rim.ref(dec["fonte"])}</p>'
    corpo += f'<p>Profili indicati dal contratto: {h("; ".join(dec["profili"]))}.</p>'
    pre, dopo = vicini(cid, L)
    rr, cl = [], []
    for x, qui in [(pre, False), (L, True), (dopo, False)]:
        if not x:
            continue
        vx = valori(cid, x)
        nome = h(x["nome"]) if qui else f'<a href="/{pagina_url(cid, x)}">{h(x["nome"])}</a>'
        rr.append((nome, euro(vx["oraria"]), euro(vx["conv"])))
        cl.append("qui" if qui else "")
    corpo += '<h2 id="vicini">Confronto con i livelli vicini</h2>' + tabella(["Livello", "Paga oraria (non convivente)", "Mensile (convivente)"], rr, classi=cl)
    corpo += ('<h2 id="non-compreso">Cosa non c\'è in queste cifre</h2><div class="testo"><ul><li>contributi INPS e Cassa Colf, che si pagano a parte ogni trimestre;</li>'
              '<li>scatti di anzianità, superminimi, straordinari e festività lavorate;</li><li>ferie e TFR maturati; il netto per il lavoratore.</li></ul></div>')
    corpo += '<p>Per chi assume: la <a href="/colf-badanti/">guida per le famiglie</a> riassume orari, vitto e alloggio, notturno e tredicesima con le cifre del 2026.</p>'
    faq_html, faq_ld = faq_blocco(f"{cid}/{L['id']}", rim)
    corpo += faq_html
    corpo += '<h2 id="altri">Gli altri livelli</h2>' + lista_livelli(cid, L)
    corpo += documento_ufficiale(cid, rim) + rim.elenco()
    titolo = titolo_livello(cid, L)
    sub = (f'Tabella ufficiale in vigore dal <strong>{data_lunga(v["dal"])}</strong>: {euro(v["oraria"])} l\'ora per chi non convive, '
           f'{euro(v["conv"])} al mese per chi convive. CCNL lavoro domestico, codice CNEL {m["codice_cnel"]}.')
    testata = banda("Colf e badanti", titolo.split(":")[0], sub)
    pagina(pagina_url(cid, L), titolo, descr_livello(cid, L, v), corpo, testata,
           briciole=[("Home", ""), (m["nome_breve"], pagina_url(cid)), (L["nome"], pagina_url(cid, L))], jsonld=[x for x in [faq_ld] if x])


# ---------------------------------------------------------------- pagina contratto
def pagina_contratto(cid):
    m = C[cid]
    rim = Rimandi()
    fa, fb = m["fonte_a"], m["fonte_b"]
    pub = livelli_pubblicati(cid)
    corpo = ""
    if cid == "domestico":
        vs = [valori(cid, L) for L in pub]
        corpo += (f'<div class="card cifre pull"><div class="cifra main"><b>{euro(vs[0]["oraria"])} – {euro(vs[-1]["oraria"])}</b><span>paga oraria, chi non convive</span></div>'
                  f'<div class="cifra"><b>{euro(vs[0]["conv"])} – {euro(vs[-1]["conv"])}</b><span>minimo mensile, chi convive</span></div>'
                  f'<div class="cifra"><b>13</b><span>mensilità (art. 39)</span></div><div class="cifra"><b>54 / 40 ore</b><span>orario massimo settimanale, convivente / non</span></div>'
                  f'<p class="asof">{ico("check")} Tabella in vigore dal {data_lunga(vs[0]["dal"])}, uguale nelle due copie ufficiali{rim.ref([fa, fb])}.</p></div>')
        righe = [(f'<a href="/{pagina_url(cid, L)}">{h(L["nome"])}</a>', euro(v["oraria"]), euro(v["conv"]) + (f" + {euro(v['ind'])}" if v["ind"] else ""),
                  euro(v["p"][20])) for L, v in zip(pub, vs)]
        corpo += '<h2 id="tabella">Minimi 2026 per livello</h2>'
        corpo += f'<p>{h(m["nota_fonti"])}{rim.ref([fa, fb])}</p>'
        corpo += tabella(["Livello", "Paga oraria (non convivente)", "Mensile (convivente)", "A 20 ore settimanali"], righe)
        corpo += '<p>Chi assume trova orari, vitto e alloggio, notturno e tredicesima nella <a href="/colf-badanti/">guida per le famiglie</a>.</p>'
    else:
        vs = [valori(cid, L) for L in pub]
        corpo += (f'<div class="card cifre pull"><div class="cifra main"><b>{len(pub)}</b><span>livelli con le cifre verificate</span></div>'
                  f'<div class="cifra"><b>÷ {m["divisore_orario"]["valore"]}</b><span>divisore orario ({h(m["divisore_orario"]["dove"].split(" del CCNL")[0])})</span></div>'
                  f'<div class="cifra"><b>{m["mensilita"]["valore"]}</b><span>mensilità ({h(m["mensilita"]["dove"].split(" del CCNL")[0])})</span></div>'
                  f'<div class="cifra"><b>{m["ore"]["valore"]} ore</b><span>orario settimanale normale</span></div>'
                  f'<p class="asof">{ico("check")} Ogni cifra è uguale in due fonti ufficiali{rim.ref([fa, fb])}. Controllato il {data_lunga(CONTROLLO)}.</p></div>')
        corpo += '<h2 id="tabella">Minimi in vigore oggi, livello per livello</h2>'
        corpo += f'<p>{h(m["nota_fonti"])}{rim.ref([fa, fb, m["testo"]["fonte"]])}</p>'
        gruppi = list(dict.fromkeys(L.get("gruppo_nome", "") for L in pub))
        for g in gruppi:
            righe = [(f'<a href="/{pagina_url(cid, L)}">{h(L["nome"])}</a>', euro(v["mensile"]), euro(v["oraria"]), data_lunga(v["dal"]))
                     for L, v in zip(pub, vs) if L.get("gruppo_nome", "") == g]
            if g:
                corpo += f"<h3>{h(g)}</h3>"
            corpo += tabella(["Livello", "Minimo al mese", "Paga oraria", "In vigore dal"], righe)
        if m.get("extra_tabella"):
            rr = []
            for x in m["extra_tabella"]:
                t = [t for t in tranche_livello_extra(cid, x["chiave"])]
                if t:
                    rr.append((h(x["nome"]), euro(t[0]["totale"])))
            if rr:
                corpo += ('<p class="small">Gli operatori di vendita hanno una tabella a parte nello stesso contratto; qui riportiamo solo il minimo mensile, '
                          f'confrontato con Filcams, senza pagina dedicata.{rim.ref([fa, fb])}</p>' + tabella(["Categoria", "Minimo al mese"], rr))
        corpo += calendario(cid, pub, rim)
    corpo += AD
    # regole
    corpo += '<h2 id="regole">Le regole del contratto usate per i calcoli</h2><div class="testo"><ul>'
    if m.get("divisore_orario"):
        d_ = m["divisore_orario"]
        corpo += f'<li><strong>Paga oraria</strong>: minimo mensile diviso {d_["valore"]} ({h(d_["dove"])}).{rim.ref(d_["fonte"])}</li>'
    if m.get("divisore_giornaliero"):
        d_ = m["divisore_giornaliero"]
        corpo += f'<li><strong>Paga giornaliera</strong>: {h(d_.get("nota") or "minimo mensile diviso " + str(d_["valore"]))} ({h(d_["dove"])}).{rim.ref(d_["fonte"])}</li>'
    elif m.get("nota_giornaliera"):
        corpo += f'<li><strong>Paga giornaliera</strong>: {h(m["nota_giornaliera"])}</li>'
    corpo += f'<li><strong>Mensilità</strong>: {m["mensilita"]["valore"]} ({h(m["mensilita"]["dove"])}).{rim.ref(m["mensilita"]["fonte"])}</li>'
    corpo += f'<li><strong>Orario</strong>: {h(m["ore"]["testo"])} ({h(m["ore"]["dove"])}).{rim.ref(m["ore"]["fonte"])}</li>'
    corpo += (f'<li><strong>Durata</strong>: testo depositato al CNEL con codice {m["codice_cnel"]}, in vigore dal {data_lunga(m["testo"]["decorrenza"])} '
              f'al {data_lunga(m["testo"]["scadenza"])}. Firmatari: {h(m["firmatari"])}.{rim.ref(m["testo"]["fonte"])}</li></ul></div>')
    if m.get("aumenti_futuri"):
        corpo += f'<h2 id="aumenti">Aumenti già firmati</h2><p>{h(m["aumenti_futuri"]["testo"])}{rim.ref(m["aumenti_futuri"]["fonte"])}</p>'
    corpo += esclusi_html(cid)
    faq_html, faq_ld = faq_blocco(cid, rim)
    corpo += faq_html
    corpo += documento_ufficiale(cid, rim) + rim.elenco()
    titolo = {"terziario": "CCNL commercio 2026: minimi e paga oraria per livello",
              "metalmeccanici": "CCNL metalmeccanici 2026: minimi e paga oraria per livello",
              "multiservizi": "CCNL multiservizi 2026: minimi e paga oraria per livello",
              "logistica": "CCNL logistica 2026: minimi e paga oraria per livello",
              "domestico": "Colf e badanti 2026: minimi per livello, a ore e conviventi"}[cid]
    descr = {"terziario": "Minimi del CCNL terziario Confcommercio dal 1° novembre 2026 e da febbraio 2027 per ogni livello, paga oraria con divisore 168, 14 mensilità.",
             "metalmeccanici": "Minimi tabellari dei metalmeccanici dal 1° giugno 2026, livelli da D1 ad A1, paga oraria con divisore 173 e tredicesima. Fonti ufficiali.",
             "multiservizi": "Minimi del CCNL pulizia e multiservizi dal 1° ottobre 2026 e tutte le rate fino al 2029, paga oraria con divisore 173, 14 mensilità.",
             "logistica": "Minimi ed EPA del CCNL logistica, trasporto merci e spedizione dal 1° gennaio 2026, aumenti del 2027 e paga oraria con divisore 168.",
             "domestico": "Tabella 2026 del lavoro domestico: paga oraria per colf e badanti non conviventi e minimo mensile per conviventi, livello per livello."}[cid]
    sub = {"domestico": "Tabella ufficiale in vigore dal 1° gennaio 2026, livello per livello, per chi convive e per chi lavora a ore."}.get(
        cid, f"{h(m['nome'])}: minimo mensile, paga oraria e aumenti già firmati per ogni livello. Codice CNEL {m['codice_cnel']}.")
    testata = banda(f"CCNL · codice CNEL {m['codice_cnel']}", titolo.split(":")[0], sub)
    pagina(pagina_url(cid), titolo, descr, corpo, testata, briciole=[("Home", ""), (m["nome_breve"], pagina_url(cid))], jsonld=[x for x in [faq_ld] if x])


def tranche_livello_extra(cid, chiave):
    """Operatori di vendita del terziario: stessa coppia di controlli, solo per la tabella della pagina contratto."""
    a = EST["terziario"]["A"]
    b = EST["terziario"]["B"]
    out = []
    for dt in sorted(a):
        if dt > OGGI.isoformat():
            continue
        ra, rb = a[dt].get(chiave), b.get(dt, {}).get(chiave)
        if not ra or not rb:
            continue
        somma = D(ra["paga_base"]) + D(ra["altri_elementi"]) + D(ra["contingenza_edr"]) == D(ra["totale"])
        uguale = (ra["paga_base"], ra["contingenza_edr"], ra["totale"]) == (rb["paga_base"], rb["contingenza"], rb["totale"])
        if somma and uguale:
            out = [{"dal": dt, "totale": ra["totale"]}]
    return out


def calendario(cid, pub, rim):
    m = C[cid]
    date_f = sorted({t["dal"] for L in pub for t in valori(cid, L)["future"] if t["pubblicabile"]})
    if not date_f:
        return ""
    intest = ["Livello", "Oggi"] + [data_lunga(d_) for d_ in date_f]
    righe = []
    for L in pub:
        v = valori(cid, L)
        per = {t["dal"]: t for t in v["future"]}
        righe.append([f'<a href="/{pagina_url(cid, L)}">{h(L["nome"])}</a>', euro(v["mensile"])] +
                     [euro(totale(per[d_])) if d_ in per and per[d_]["pubblicabile"] else "—" for d_ in date_f])
    out = '<h2 id="calendario">Calendario degli aumenti già firmati</h2>'
    out += f'<p>Minimo mensile di ogni livello alle date già scritte nel contratto. Il trattino indica una cifra che non pubblichiamo (vedi sotto).{rim.ref([m["fonte_a"], m["fonte_b"]])}</p>'
    return out + tabella(intest, righe)


def esclusi_html(cid):
    righe = []
    for L in C[cid]["livelli"]:
        for t in tranche_livello(cid, L["id"]):
            if not t["pubblicabile"] and not (cid == "metalmeccanici" and t["dal"] > OGGI.isoformat()):
                righe.append((h(L["nome"]), data_lunga(t["dal"]), h("; ".join(t["motivi"]))))
    if not righe:
        return ('<h2 id="esclusi">Cifre escluse</h2><p>Per questo contratto tutte le cifre lette hanno passato i due controlli: la somma delle voci '
                'e il confronto con la seconda fonte.</p>')
    return ('<h2 id="esclusi">Cifre che non pubblichiamo</h2><p>Queste righe sono nei documenti ufficiali ma non passano i nostri controlli. Non le correggiamo '
            'a mano e non le stimiamo: restano fuori finché una fonte ufficiale non le chiarisce.</p>'
            + tabella(["Livello", "Dal", "Motivo"], righe, num=[]))


# ---------------------------------------------------------------- guida per le famiglie
def colf_badanti():
    m = C["domestico"]
    rim = Rimandi()
    fa, fb = m["fonte_a"], m["fonte_b"]
    A = EST["domestico"]["A"]
    pub = livelli_pubblicati("domestico")
    vs = {L["id"]: valori("domestico", L) for L in pub}
    corpo = (f'<div class="card cifre pull"><div class="cifra main"><b>{euro(vs["b"]["oraria"])}</b><span>l\'ora per una colf di livello B a ore</span></div>'
             f'<div class="cifra"><b>{euro(vs["cs"]["conv"])}</b><span>al mese per una badante convivente CS</span></div>'
             f'<div class="cifra"><b>{euro(A["BS"]["F_totale"])}</b><span>al giorno per vitto e alloggio non dati</span></div>'
             f'<div class="cifra"><b>13</b><span>mensilità: c\'è la tredicesima</span></div>'
             f'<p class="asof">{ico("check")} Tabella ufficiale in vigore dal 1° gennaio 2026{rim.ref([fa, fb])}.</p></div>')
    corpo += '<h2 id="livello">1. Scegliere il livello giusto</h2>'
    corpo += f'<p>Il livello dipende da cosa fa la persona, non da quante ore lavora. Il contratto (art. 9) indica questi profili.{rim.ref("cnel_245143")}</p>'
    righe = [(f'<a href="/{pagina_url("domestico", L)}">{h(L["nome"])}</a>', h("; ".join(L["declaratoria"]["profili"][:3])), euro(vs[L["id"]]["oraria"]), euro(vs[L["id"]]["conv"]))
             for L in pub]
    corpo += tabella(["Livello", "Esempi di profili", "All'ora (non convivente)", "Al mese (convivente)"], righe, num=[2, 3])
    corpo += '<h2 id="orario">2. Convivente o a ore: cosa cambia</h2><div class="testo"><ul>'
    corpo += (f'<li><strong>Convivente</strong>: stipendio mensile fisso (tabella A) per un orario fino a 10 ore al giorno non consecutive e 54 a settimana, '
              f'con vitto e alloggio e almeno 11 ore di riposo consecutivo al giorno (art. 14).{rim.ref("cnel_245143")}</li>')
    corpo += (f'<li><strong>Convivente fino a 30 ore</strong>: per i livelli B, BS e C c\'è una tabella apposita (tabella B): {euro(A["B"]["B_mensile"])}, '
              f'{euro(A["BS"]["B_mensile"])} e {euro(A["C"]["B_mensile"])} al mese.{rim.ref(fa)}</li>')
    corpo += (f'<li><strong>Non convivente (a ore)</strong>: paga oraria (tabella C) per un massimo di 8 ore al giorno e 40 a settimana. Il mensile si calcola '
              f'come paga oraria × ore a settimana × 52 ÷ 12.{rim.ref("cnel_245143")}</li></ul></div>')
    # calcolatore con scelta del livello: un riquadro di esempio (livello B) con link alle altre pagine
    corpo += calcolatore(vs["b"], "orario52", 13, "Colf di livello B a ore: il minimo al mese", "Ore a settimana (massimo 40)", 40,
                         f'Esempio con il livello B ({euro(vs["b"]["oraria"])} l\'ora). Per un altro livello apri la sua pagina: ogni pagina ha lo stesso calcolo. Lordo, senza contributi.')
    corpo += AD
    rr = [(f'<a href="/{pagina_url("domestico", L)}">{h(L["nome"])}</a>', euro(vs[L["id"]]["p"][10]), euro(vs[L["id"]]["p"][20]), euro(vs[L["id"]]["p"][30])) for L in pub]
    corpo += '<h3>Minimo mensile a ore, per livello</h3>' + tabella(["Livello", "10 ore", "20 ore", "30 ore"], rr)
    corpo += '<h2 id="vitto">3. Vitto e alloggio</h2>'
    f_ = A["BS"]
    corpo += (f'<p>Per chi convive, vitto e alloggio fanno parte della retribuzione. Se non vengono dati, si pagano in denaro con i valori della tabella F '
              f'(uguali per tutti i livelli).{rim.ref([fa, fb])}</p>')
    corpo += tabella(["Voce", "Valore al giorno"], [("Pranzo o colazione", euro(f_["F_pranzo"])), ("Cena", euro(f_["F_cena"])), ("Alloggio", euro(f_["F_alloggio"])),
                                                     ("<strong>Totale stampato</strong>", f'<strong>{euro(f_["F_totale"])}</strong>')],
                     caption=f'Controllo: {euro(f_["F_pranzo"])} + {euro(f_["F_cena"])} + {euro(f_["F_alloggio"])} = {euro(f_["F_totale"])}, come il totale stampato.')
    corpo += (f'<p>Chi lavora almeno 6 ore al giorno con presenza continuativa ha diritto al pasto o, se non è dato, al suo valore (art. 14, comma 8).{rim.ref("cnel_245143")}</p>')
    corpo += '<h2 id="notte">4. Notte e sostituzioni</h2><div class="testo"><ul>'
    corpo += (f'<li><strong>Assistenza notturna discontinua</strong> tra le 20 e le 8 (art. 10, tabella D): {euro(A["BS"]["D_autosuff"])} al mese per persone '
              f'autosufficienti (livello BS); {euro(A["CS"]["D_non_autosuff"])} (CS) e {euro(A["DS"]["D_non_autosuff"])} (DS) per persone non autosufficienti.{rim.ref(fa)}</li>')
    corpo += (f'<li><strong>Sola presenza notturna</strong> tra le 21 e le 8, con riposo completo (art. 11, tabella E): {euro(A["unico"]["E_mensile"])} al mese, livello unico.{rim.ref(fa)}</li>')
    corpo += (f'<li><strong>Sostituzione nei riposi</strong> della badante titolare di livello CS o DS (art. 14, comma 9, tabella G): {euro(A["CS"]["G_oraria"])} '
              f'e {euro(A["DS"]["G_oraria"])} l\'ora.{rim.ref(fa)}</li></ul></div>')
    corpo += '<h2 id="indennita">5. Indennità che si aggiungono</h2><div class="testo"><ul>'
    corpo += (f'<li>Baby sitter (livello BS) con bambini sotto i 6 anni: {euro(A["BS"]["H_mensile"])} al mese (tabella H, art. 34 c. 3).{rim.ref(fa)}</li>'
              f'<li>Badante CS o DS che assiste più persone non autosufficienti: {euro(A["CS"]["I_mensile"])} al mese (tabella I, art. 34 c. 4).{rim.ref(fa)}</li>'
              f'<li>Livelli B, BS e CS con certificazione UNI 11766: {euro(A["B"]["L_mensile"])} al mese (tabella L, art. 34 c. 7).{rim.ref(fa)}</li>'
              f'<li>Livelli D e DS: indennità di funzione di {euro(A["D"]["A_indennita"])} al mese, che fa parte del minimo (art. 34 c. 2).{rim.ref([fa, "cnel_245143"])}</li></ul></div>')
    corpo += '<h2 id="tredicesima">6. Tredicesima e aumenti</h2>'
    corpo += (f'<p>A dicembre spetta una mensilità in più, che comprende anche il valore di vitto e alloggio; chi ha lavorato meno di un anno ne riceve '
              f'tanti dodicesimi quanti sono i mesi (art. 39).{rim.ref("cnel_245143")} {h(m["aumenti_futuri"]["testo"])}{rim.ref(m["aumenti_futuri"]["fonte"])}</p>')
    corpo += nota("Queste sono le cifre minime della retribuzione. Il costo per la famiglia è più alto: si aggiungono i contributi INPS e Cassa Colf (trimestrali), "
                  "le ferie, il TFR e le eventuali festività lavorate. Qui non li calcoliamo.", "", "alert")
    faq_html, faq_ld = faq_blocco("colf-badanti", rim)
    corpo += faq_html
    corpo += f'<h2 id="livelli">Le pagine dei livelli</h2>' + lista_livelli("domestico")
    corpo += documento_ufficiale("domestico", rim) + rim.elenco()
    titolo = "Assumere colf o badante: minimi 2026, orari e vitto"
    testata = banda("Guida per le famiglie", "Colf e badanti: quanto spetta nel 2026",
                    "Per chi assume: livello, convivenza o ore, vitto e alloggio, notte e tredicesima, con le cifre della tabella ufficiale 2026.", icona="home")
    pagina("colf-badanti/", titolo, "Guida per le famiglie che assumono colf o badanti: minimi 2026 per livello, convivente o a ore, vitto e alloggio, notturno e tredicesima.",
           corpo, testata, briciole=[("Home", ""), ("Colf e badanti", "colf-badanti/")], jsonld=[x for x in [faq_ld] if x])


# ---------------------------------------------------------------- home
SINONIMI = {"terziario": "commercio terziario confcommercio distribuzione servizi negozio commessa",
            "metalmeccanici": "metalmeccanici metalmeccanico industria federmeccanica operaio",
            "multiservizi": "multiservizi pulizie pulizia servizi integrati",
            "logistica": "logistica trasporto merci spedizione autista magazziniere driver rider",
            "domestico": "colf badante badanti baby sitter lavoro domestico"}


def chiavi_livello(L):
    n = L["nome"].lower()
    extra = []
    m_ = re.match(r"(\d)° livello", n)
    if m_:
        extra += [f"{m_.group(1)} livello", f"livello {m_.group(1)}", ["", "primo", "secondo", "terzo", "quarto", "quinto", "sesto", "settimo"][int(m_.group(1))]]
    m_ = re.match(r"livello ([a-z]+\d?)", n)
    if m_:
        extra.append(m_.group(1))
    return n + " " + " ".join(extra)


def home():
    rim = Rimandi()
    blocchi = ""
    n = 0
    for cid in ORDINE:
        m = C[cid]
        righe = ""
        for L in livelli_pubblicati(cid):
            v = valori(cid, L)
            n += 1
            if cid == "domestico":
                cifra, ora = euro(v["conv"]) + ' <span class="small">convivente</span>', euro(v["oraria"])
            else:
                cifra, ora = euro(v["mensile"]), euro(v["oraria"])
            righe += (f'<tr data-riga="{h(SINONIMI[cid] + " " + chiavi_livello(L))}"><td><a href="/{pagina_url(cid, L)}">{h(L["nome"])}</a></td>'
                      f'<td class="n">{cifra}</td><td class="n">{ora}</td><td class="n nascondi-m">{data_lunga(v["dal"])}</td></tr>')
        div_ = f'divisore {m["divisore_orario"]["valore"]}' if m.get("divisore_orario") else "paga oraria da tabella"
        blocchi += (f'<section data-blocco><div class="contratto-h"><h2 id="{cid}"><a href="/{pagina_url(cid)}">{h(m["nome_breve"])}</a></h2>'
                    f'<span class="small">CNEL {m["codice_cnel"]} · {div_}</span></div>'
                    f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Livello</th><th scope="col" class="n">Minimo al mese</th>'
                    f'<th scope="col" class="n">Paga oraria</th><th scope="col" class="n nascondi-m">In vigore dal</th></tr></thead><tbody>{righe}</tbody></table></div></section>')
    cerca = ('<form class="cerca" role="search" onsubmit="return false"><label for="q" class="hp">Cerca contratto o livello</label>'
             '<input id="q" type="search" data-cerca placeholder="Cerca: commercio 4 livello, C3, badante CS…" autocomplete="off"></form>')
    testata = banda("Minimi contrattuali 2026", "Paga oraria e minimo per contratto e livello",
                    f"Le cifre di <strong>{n} livelli</strong> di 5 contratti nazionali, ognuna confrontata al centesimo su due fonti ufficiali. Lordo, senza netto né stime.",
                    extra=cerca)
    corpo = (f'<div class="card pull"><p style="margin:0">Scrivi il tuo contratto e il livello per filtrare la tabella. Ogni livello ha una pagina con le voci del minimo, '
             f'la formula della paga oraria con l\'articolo del contratto, il calcolo per 20, 24, 30 ore e gli aumenti già firmati.</p></div>')
    corpo += blocchi + '<p class="vuoto-ricerca" data-vuoto hidden>Nessun livello trovato. Prova con il nome del contratto (commercio, metalmeccanici, multiservizi, logistica, colf).</p>'
    corpo += AD
    corpo += '<h2 id="come">Come leggiamo le cifre</h2><div class="testo">'
    corpo += (f'<p>Per ogni contratto usiamo due fonti indipendenti: il testo depositato al CNEL e le tabelle del Ministero del Lavoro, oppure l\'accordo pubblicato '
              f'da una delle parti firmatarie. Una cifra entra nel sito solo se le voci sommano al totale stampato e se la seconda fonte riporta lo stesso importo. '
              f'Se qualcosa non torna, la riga resta fuori e lo scriviamo nella pagina del contratto.{rim.ref(["cnel_246574", "filcams_minimi", "min_dd94_impiegati", "min_dd25_operai", "min_dd135", "min_domestico_2026"])}</p>'
              f'<p>La paga oraria si ottiene dividendo il minimo mensile per il divisore che il contratto scrive in un articolo preciso: 168 nel commercio e nella logistica, '
              f'173 nei metalmeccanici e nel multiservizi. Per colf e badanti a ore la paga oraria è già nella tabella ufficiale.</p>'
              f'<p>Le cifre sono lorde e minime: niente netto, niente scatti di anzianità o superminimi. Per chi assume una colf o una badante c\'è una '
              f'<a href="/colf-badanti/">guida per le famiglie</a>.</p></div>')
    corpo += '<h2 id="contratti">I contratti</h2><ul class="griglia">' + "".join(
        f'<li><a href="/{pagina_url(c)}"><b>{h(C[c]["nome_breve"])}</b><span>{h(C[c]["nome"])}</span><span>{len(livelli_pubblicati(c))} livelli · CNEL {C[c]["codice_cnel"]}</span></a></li>'
        for c in ORDINE) + '<li><a href="/colf-badanti/"><b>Colf e badanti</b><span>Guida per le famiglie che assumono</span><span>orari, vitto, notte, tredicesima</span></a></li></ul>'
    faq_html, faq_ld = faq_blocco("home", rim)
    corpo += faq_html + rim.elenco()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/", "inLanguage": "it"}] + ([faq_ld] if faq_ld else [])
    pagina("", "Paga CCNL: minimi e paga oraria per contratto e livello",
           "Minimi contrattuali 2026 e paga oraria per livello: commercio, metalmeccanici, multiservizi, logistica, colf e badanti. Due fonti ufficiali per ogni cifra.",
           corpo, testata.replace("{bc}", ""), jsonld=ld)


# ---------------------------------------------------------------- pagine del sito
MODULO = """<form name="segnalazioni" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card">
<input type="hidden" name="form-name" value="segnalazioni">
<p class="hp"><label>Lascia vuoto questo campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Pagina o cifra<input type="text" name="pagina" required maxlength="300" placeholder="Per esempio /terziario-commercio/4-livello/"></label>
<label>Cosa non torna?<textarea name="messaggio" required rows="5" maxlength="3000"></textarea></label>
<label>Fonte ufficiale (facoltativa)<input type="url" name="fonte" maxlength="500" placeholder="https://"></label>
<label>La tua email (facoltativa, solo se vuoi una risposta)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>Accetto che il messaggio, e l'email se l'ho scritta, siano conservati per controllare e rispondere alla segnalazione (vedi la <a href="/privacy/#segnalazioni">privacy</a>).</span></label>
<button type="submit" class="btn">Invia la segnalazione</button>
</form>"""


def come_lavoriamo():
    rim = Rimandi()
    tot = pub = 0
    for cid in RIS:
        for L in RIS[cid]["livelli"]:
            for t in L["tranche"]:
                tot += 1
                pub += t["pubblicabile"]
    ncorr = len(carica("correzioni_ocr.json")["correzioni"])
    corpo = (f'<div class="card pull"><p style="margin:0"><strong>Ogni cifra del sito viene da due fonti ufficiali e deve essere uguale in entrambe, al centesimo.</strong> '
             f'Il {data_lunga(CONTROLLO)} abbiamo letto {len(FONTI)} documenti ufficiali e confrontato {tot} righe di tabella (livello per data): '
             f'{pub} hanno passato i controlli, {tot - pub} restano fuori con il motivo scritto.</p></div>')
    corpo += '<h2 id="regola">La regola: somma e seconda fonte</h2><div class="testo"><ol>'
    corpo += ('<li><strong>La somma.</strong> Quando la tabella stampa le voci (paga base, contingenza, elemento d\'area…) e il totale, le voci devono sommare al totale. '
              'Se non tornano, la riga non si pubblica, anche se l\'errore è di pochi centesimi.</li>'
              '<li><strong>La seconda fonte.</strong> La stessa cifra deve comparire in un secondo documento indipendente: per esempio il testo del contratto e la '
              'tabella del Ministero del Lavoro. Le tabelle del Ministero danno importi annui: li dividiamo per 12 e controlliamo che la divisione sia esatta.</li>'
              '<li><strong>Le regole di calcolo.</strong> Divisore orario, divisore giornaliero, mensilità e orario vengono da una frase precisa del contratto, '
              'che i nostri controlli ritrovano nel testo ufficiale a ogni aggiornamento.</li></ol></div>')
    corpo += '<h2 id="contratti">Le due fonti di ogni contratto</h2>'
    rr = [(f'<a href="/{pagina_url(c)}">{h(C[c]["nome_breve"])}</a>', h(FONTI_DEF[C[c]["fonte_a"]]["titolo"]) + rim.ref(C[c]["fonte_a"]),
           h(FONTI_DEF[C[c]["fonte_b"]]["titolo"]) + rim.ref(C[c]["fonte_b"])) for c in ORDINE]
    corpo += tabella(["Contratto", "Fonte A", "Fonte B"], rr, num=[])
    corpo += '<h2 id="ocr">Quando il documento è una scansione</h2><div class="testo">'
    corpo += (f'<p>Alcuni documenti sono scansioni o usano caratteri che non si estraggono come testo (le tabelle del testo unico del commercio, l\'accordo dei '
              f'metalmeccanici del 22 novembre 2025, l\'accordo integrativo del multiservizi). Li leggiamo con un programma di lettura ottica (in italiano). '
              f'Dove la lettura sbaglia una cifra, la correggiamo guardando l\'immagine della pagina e lo annotiamo: oggi sono {ncorr} valori, tutti nell\'accordo del '
              f'multiservizi. Anche i valori corretti devono poi passare la somma e il confronto con la seconda fonte.{rim.ref(["cnel_246574", "fm_accordo_2025", "cnel_234752"])}</p></div>')
    corpo += '<h2 id="esclusi">Cosa abbiamo lasciato fuori</h2><div class="testo"><ul>'
    corpo += ('<li><strong>Logistica, livello F2 (viaggiante)</strong>: nel testo del contratto minimo più EPA non danno il totale stampato (6 centesimi di differenza a ogni data).</li>'
              '<li><strong>Logistica, personale non viaggiante dal 1° gennaio 2027</strong>: i totali stampati usano già il minimo di giugno 2027; le voci coincidono con il Ministero ma il totale no.</li>'
              '<li><strong>Logistica, livello L nei primi 6 mesi</strong>: il Ministero stampa un elemento d\'area diverso da quello del contratto.</li>'
              '<li><strong>Metalmeccanici, minimi di giugno 2027 e 2028</strong>: sono solo nell\'accordo di rinnovo e possono salire con l\'inflazione; li pubblichiamo quando arriva il decreto del Ministero.</li>'
              '<li><strong>Multiservizi, 2° livello con parametro 115</strong>: compare nelle tabelle del Ministero ma l\'accordo non ne stampa il minimo.</li>'
              '<li><strong>Il netto in busta paga</strong>: dipende da detrazioni, addizionali e situazione familiare. Non lo stimiamo.</li></ul></div>')
    corpo += '<h2 id="fonti-elenco">I documenti letti</h2>'
    rr = []
    for fid, f in FONTI_DEF.items():
        es = FONTI[fid]
        rr.append((f'<a href="{h(es["url"])}" rel="noopener">{h(f["titolo"])}</a>', h(f["chi"]), str(es.get("pagine") or "pagina web"),
                   data_lunga(es["letto_il"]), f'<code>{es["sha256"][:12]}</code>'))
    corpo += tabella(["Documento", "Chi lo pubblica", "Pagine", "Letto il", "Impronta"], rr, num=[2],
                     caption="L'impronta (SHA-256, prime 12 cifre) identifica il file letto: se il documento cambia, cambia l'impronta e lo ricontrolliamo.")
    corpo += '<h2 id="aggiornamenti">Ogni quanto aggiorniamo</h2><div class="testo"><ul>'
    corpo += ('<li><strong>Ogni mese</strong> rileggiamo il file aperto dell\'archivio del CNEL e guardiamo se per uno dei contratti seguiti è stato depositato un accordo nuovo; '
              'rileggiamo anche le pagine di settore del Ministero del Lavoro.</li>'
              '<li><strong>A gennaio</strong> arriva la nuova tabella del lavoro domestico; <strong>a giugno</strong> l\'adeguamento dei metalmeccanici e poi il decreto del Ministero.</li>'
              '<li>Gli aumenti già firmati sono caricati con la loro data: la pagina mostra il nuovo minimo dal giorno in cui entra in vigore, alla prima pubblicazione utile.</li></ul></div>')
    corpo += ('<h2 id="segnala">Segnala un errore</h2><p>Hai trovato una cifra che non coincide con il documento ufficiale? Scrivici la pagina e, se puoi, il link alla fonte. '
              'Controlliamo sulla fonte ufficiale, non sulla segnalazione da sola. L\'email è facoltativa.</p>' + MODULO)
    corpo += rim.elenco()
    testata = banda("Come lavoriamo", "Come leggiamo e controlliamo le cifre", "Due fonti ufficiali per ogni importo, la somma delle voci, la lettura delle scansioni e cosa resta fuori.", corta=True, icona="shield")
    pagina("come-lavoriamo/", "Come lavoriamo: fonti, controlli e correzioni | Paga CCNL",
           "Come Paga CCNL legge i minimi dei contratti: due fonti ufficiali per ogni cifra, controllo delle somme, lettura delle scansioni e cifre escluse.",
           corpo, testata, briciole=[("Home", ""), ("Come lavoriamo", "come-lavoriamo/")])


def chi_siamo():
    corpo = ('<div class="card pull testo"><p><strong>Paga CCNL è un sito informativo indipendente e gratuito.</strong> Mette in pagine semplici i minimi dei contratti '
             'collettivi nazionali, livello per livello, con la paga oraria calcolata come dice il contratto e il link ai documenti ufficiali.</p></div>'
             '<h2>Perché esiste</h2><div class="testo"><p>Le tabelle dei minimi stanno in PDF di centinaia di pagine, spesso scansionati, oppure nelle tabelle del costo '
             'del lavoro del Ministero, scritte in importi annui. Chi cerca «quanto prende un 4° livello a 30 ore» o «paga oraria colf 2026» trova cifre diverse da '
             'un sito all\'altro. Qui ogni cifra ha accanto le sue due fonti.</p></div>'
             '<h2>Cosa non siamo</h2><div class="testo"><ul><li>Non siamo il CNEL, il Ministero del Lavoro, un sindacato o un\'associazione di imprese, e non siamo '
             'legati a nessuno di loro.</li><li>Non facciamo consulenza del lavoro e non calcoliamo il netto in busta paga.</li><li>Non raccogliamo dati di chi legge, '
             'a parte il modulo facoltativo per segnalare un errore.</li></ul></div>'
             '<h2>Come si sostiene</h2><div class="testo"><p>Il sito può mostrare pubblicità di Google AdSense. La pubblicità non cambia nessuna cifra e nessuno '
             'paga per comparire.</p><p>Paga CCNL fa parte di una piccola rete di siti informativi gratuiti dello stesso gestore. Come controlliamo le cifre: '
             '<a href="/come-lavoriamo/">come lavoriamo</a>.</p></div>')
    testata = banda("Chi siamo", "Chi siamo", "Un sito indipendente che rende leggibili i minimi dei contratti nazionali.", corta=True, icona="info")
    pagina("chi-siamo/", "Chi siamo | Paga CCNL", "Paga CCNL è un sito indipendente e gratuito con i minimi dei contratti nazionali per livello, presi da due fonti ufficiali.",
           corpo, testata, briciole=[("Home", ""), ("Chi siamo", "chi-siamo/")])


def privacy():
    cookie = MON.privacy_cookie("it", SITO_ID) or ('<h2>Cookie e contatore visite</h2><p>Per contare le visite usiamo GoatCounter, che non usa cookie. '
                                                  'Il sito non usa cookie di profilazione e non mostra pubblicità.</p>')
    corpo = ('<div class="card pull testo"><p>Questa pagina spiega quali dati tratta Paga CCNL (paga-ccnl.netlify.app). In breve: pochissimi.</p></div>'
             '<div class="testo"><h2>Il calcolo in pagina</h2><p>Il calcolo per ore settimanali avviene nel tuo browser: le ore che scrivi non vengono inviate né salvate. '
             'Il sito ricorda nel browser solo la scelta del tema chiaro o scuro (memoria locale).</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>Il sito è ospitato da Netlify, che tratta dati tecnici (come l\'indirizzo IP) per consegnare le pagine e proteggere il servizio.</p>'
             '<h2 id="segnalazioni">Modulo «Segnala un errore»</h2><p>Se usi il modulo riceviamo la pagina che indichi, il messaggio, il link alla fonte e, solo se la scrivi, '
             'la tua email. Il modulo è gestito da Netlify Forms per nostro conto. Usiamo questi dati solo per controllare la segnalazione e, se hai lasciato l\'email, '
             'risponderti; li cancelliamo quando la segnalazione è chiusa. La base giuridica è il consenso dato con la casella del modulo; puoi chiedere la '
             'cancellazione con un\'altra segnalazione. Non ci sono account né newsletter.</p>'
             '<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione e cancellazione dei dati (artt. 15-22 GDPR) e fare reclamo al Garante per la protezione dei dati '
             'personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>'
             f'<h2>Modifiche</h2><p>Aggiorniamo questa pagina quando il sito cambia. Ultimo aggiornamento: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("it", SITO_ID) or "Cosa raccogliamo (pochissimo) e come funziona il contatore delle visite."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", "Privacy | Paga CCNL", "Privacy di Paga CCNL: calcolo nel browser, contatore delle visite senza cookie e pubblicità di Google solo con il tuo consenso.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = ('<div class="card pull"><p>La pagina che cerchi non esiste. Torna alla <a href="/">tabella di tutti i livelli</a> oppure scegli un contratto.</p></div>'
             '<ul class="griglia" style="margin-top:20px">' + "".join(f'<li><a href="/{pagina_url(c)}"><b>{h(C[c]["nome_breve"])}</b><span>CNEL {C[c]["codice_cnel"]}</span></a></li>' for c in ORDINE) + "</ul>")
    testata = banda("Errore 404", "Pagina non trovata", "Questo indirizzo non ha una pagina.", corta=True, icona="alert")
    pagina("", "Pagina non trovata | Paga CCNL", "Pagina non trovata.", corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{CONTROLLO.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in ccnl/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = ccnl/sito, Build command vuoto, Publish directory = "."
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


def controlli():
    err = []
    for fid, es in FONTI.items():
        if es.get("http") != 200:
            err.append(f"fonte {fid}: HTTP {es.get('http')}")
        manca = [c for c, ok in es.get("trovate", {}).items() if not ok]
        if manca:
            err.append(f"fonte {fid}: frasi non trovate {manca}")
    for cid in C:
        for L in C[cid]["livelli"]:
            cur, _, _ = stato_livello(cid, L)
            if cur is None:
                err.append(f"{cid}/{L['id']}: nessuna tabella in vigore")
    # una data di aumento esclusa che diventa "in vigore" blocca la pagina: va aggiornata a mano (NOTE.md)
    for cid in C:
        for L in C[cid]["livelli"]:
            cur, _, _ = stato_livello(cid, L)
            if cur and not cur["pubblicabile"] and cur["dal"] > CONTROLLO.isoformat():
                err.append(f"{cid}/{L['id']}: dal {cur['dal']} la tabella in vigore non passa i controlli ({'; '.join(cur['motivi'])}): aggiornare le fonti")
    if OGGI >= date(2027, 1, 1):
        err.append("lavoro domestico: dal 1° gennaio 2027 serve la nuova tabella del Ministero (NOTE.md)")
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
    for cid in ORDINE:
        pagina_contratto(cid)
        for L in livelli_pubblicati(cid):
            (pagina_domestico if cid == "domestico" else lambda x: pagina_livello(cid, x))(L)
    colf_badanti()
    come_lavoriamo()
    chi_siamo()
    privacy()
    pagina_404()
    extra()
    n_liv = sum(len(livelli_pubblicati(c)) for c in ORDINE)
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404 ({n_liv} pagine livello). Fonti controllate il {data_lunga(CONTROLLO)}.")


if __name__ == "__main__":
    main()
