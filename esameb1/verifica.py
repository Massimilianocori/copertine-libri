"""Controllo del sito generato di EsameB1 (esameb1/sito/), da lanciare dopo python3 esameb1/genera.py.

Uso (dalla radice del repository):
    python3 esameb1/verifica.py        # stampa il riepilogo; esce con 1 se c'è almeno un errore

Controlla, su tutte le pagine HTML:
- meta di verifica di Search Console (entrambe le proprietà), canonical giusto, un solo h1;
- sitemap e noindex coerenti (una pagina noindex non è in sitemap, una pagina in indice sì; la 404 è esclusa);
- sitemap.xml indice di sitemap di sezione, lastmod uguale al registro dati/lastmod.json, robots.txt con il solo indice,
  sitemap-vecchi-indirizzi.xml fuori dall'indice e con soli vecchi indirizzi vivi; la home non linka pagine noindex (25/11/2026);
- AdSense mai nelle pagine noindex; cancello della pubblicità rifatto qui (controlli_cancello): niente script e niente link di
  affiliazione sotto la soglia di parole proprie, niente script nelle privacy, script nella home;
- JSON-LD valido; ogni domanda e risposta del FAQPage è visibile nel testo della pagina;
- link interni e ancore (#id) esistenti;
- titoli ≤ 65 e description ≤ 155 caratteri, nessun titolo o description doppi tra le pagine in indice;
- nessuna parola di servizio rimasta nel testo (TODO, None, undefined, NaN, nomi di modelli).
- pagine CPIA (/cpia/<slug>/, dal 20/11/2026) contro dati/cpia.json e dati/parole_cpia.json: una pagina per ogni CPIA dei dati e nessuna in più,
  titolo che comincia con la ricerca misurata (volume > 0), codice della scuola e tutte le sedi dell'anagrafe in pagina, fonte del Ministero
  con data di lettura, ogni testo tra «» uguale a una frase citata nei dati, riquadro del libro con l'etichetta libro-cpia e nessun link sponsorizzato.
Nato dallo script di controllo usato nelle revisioni del 31/10-12/11/2026 (scratchpad), scritto qui il 13/11/2026.
"""
import collections
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlparse

SITO = Path(__file__).resolve().parent / "sito"
URL = "https://esameb1.eu/"
VERIFICHE = ("btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI", "oqTPjb5TjEbrEBUVj-ToW2AiPp1Vw85qL8ZHibY28FI")
VIETATE = ("TODO", "Lorem", "None", "undefined", "NaN", " null ", "Claude", "GPT", "Anthropic", "Gemini")


def testo(h):
    h = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", h)))


def controlli_cpia(err):
    """Pagine /cpia/<slug>/ contro i dati: vedi l'elenco in cima al file. Restituisce il numero di pagine CPIA controllate."""
    dati = SITO.parent / "dati"
    if not (dati / "cpia.json").exists():
        return 0
    D = json.loads((dati / "cpia.json").read_text(encoding="utf-8"))
    volumi = json.loads((dati / "parole_cpia.json").read_text(encoding="utf-8"))["parole"]
    attese = {c["slug"] for c in D["cpia"]}
    trovate = {p.parent.name for p in (SITO / "cpia").glob("*/index.html")}
    for sl in sorted(attese ^ trovate):
        err.append(f"cpia/{sl}/: pagina senza dati o dati senza pagina")
    if not (SITO / "cpia" / "index.html").exists():
        err.append("cpia/index.html: manca l'indice dei CPIA")
    giorno, mese, anno = int(D["anagrafe"]["letta_il"][8:]), int(D["anagrafe"]["letta_il"][5:7]), D["anagrafe"]["letta_il"][:4]
    mesi = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
    letta = f"{giorno} {mesi[mese - 1]} {anno}"
    for c in D["cpia"]:
        f = SITO / "cpia" / c["slug"] / "index.html"
        if not f.exists():
            continue
        h = f.read_text(encoding="utf-8")
        rel = f"cpia/{c['slug']}/index.html"
        corpo = h[h.find("<main"):h.find("</main>")]
        t = testo(corpo)
        titolo = unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))
        if not volumi.get(c["ricerca"], 0) > 0 or not titolo.lower().startswith(c["ricerca"].lower()):
            err.append(f"{rel}: il titolo non comincia con una ricerca misurata («{c['ricerca']}»)")
        if not re.fullmatch(r"[A-Z]{2}MM[0-9A-Z]{6}", c["codice"]) or c["codice"] not in t:
            err.append(f"{rel}: codice della scuola assente o non valido")
        for s in c["sedi"]:
            if s["codice"] not in t or s["cap"] not in t or "Non Disponibile" in t or "CARCER" in (s["nome"] + " " + s["indirizzo"]).upper():
                err.append(f"{rel}: sede {s['codice']} dell'anagrafe non in pagina")
        if "dati.istruzione.it" not in corpo or f"letta il {letta}" not in t:
            err.append(f"{rel}: manca la fonte del Ministero con la data di lettura")
        citate = {re.sub(r"\s+", " ", x["testo"]) for voci in c["citazioni"].values() for x in voci} | {c["nome_anagrafe"], "Centro territoriale"}
        avvisi = {x["citazione"] for x in json.loads((dati / "avvisi_sedi.json").read_text(encoding="utf-8"))["avvisi"]}  # avviso ufficiale di una sede
        for frase in re.findall(r"«([^»]+)»", t):
            if frase.strip() not in citate | avvisi:
                err.append(f"{rel}: testo tra virgolette non citato nei dati: {frase[:60]}")
        for x in citate - {"Centro territoriale"}:
            if x not in t:
                err.append(f"{rel}: frase dei dati non in pagina: {x[:60]}")
        libro = re.findall(r'<a [^>]*data-libro-proprio="si"[^>]*>', corpo)
        if not libro or any('data-goatcounter-click="esameb1.eu/clic/libro-cpia"' not in x for x in libro):
            err.append(f"{rel}: riquadro del libro assente o con un'altra etichetta")
        if "sponsored" in corpo:
            err.append(f"{rel}: link sponsorizzato in una pagina CPIA")
        for tema, parola in (("test_a2", "test A2"), ("certificazioni", "esami")):
            if not c["citazioni"].get(tema) and parola in titolo:
                err.append(f"{rel}: il titolo promette «{parola}» ma nei dati non c'è una frase del CPIA")
    return len(attese & trovate)


SOGLIA_PAROLE_PROPRIE = 110  # la stessa di genera.py (MIN_PAROLE_PROPRIE_ADSENSE): qui è scritta a mano apposta, mai sotto 100
SCRIPT_ADSENSE = "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"


def controlli_cancello(err):
    """Cancello della pubblicità (26/11/2026), misura rifatta qui senza usare genera.py: parole proprie = parole del <main> (senza
    riquadro di affiliazione, briciole, script, stili, icone, menu a tendina) fuori da ogni gruppo di 5 parole presente in almeno
    3 pagine. Ogni pagina sotto la soglia: niente script AdSense e niente link rel="sponsored". Ogni pagina con lo script: sopra la
    soglia, in indice, non privacy. La home ha lo script. L'elenco coincide con dati/cancello_pubblicita.json.
    Restituisce (pagine con script, pagine sotto la soglia)."""
    testi = {}
    for f in sorted(SITO.rglob("*.html")):
        h = f.read_text(encoding="utf-8")
        m = re.search(r"<main[^>]*>(.*?)</main>", h, re.S)
        if not m:
            continue
        corpo = re.sub(r'<section class="card prep".*?</section>', " ", m.group(1), flags=re.S)
        corpo = re.sub(r"<(nav|script|style|svg|select)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
        testi[str(f.relative_to(SITO))] = (re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", corpo)).lower()), h)
    quante = collections.Counter()
    gruppi = {}
    for rel, (w, _) in testi.items():
        gruppi[rel] = [tuple(w[i:i + 5]) for i in range(len(w) - 4)]
        quante.update(set(gruppi[rel]))
    sotto, con_script = {}, 0
    for rel, (w, h) in testi.items():
        comune = [False] * len(w)
        for i, g in enumerate(gruppi[rel]):
            if quante[g] >= 3:
                comune[i:i + 5] = [True] * 5
        proprie = comune.count(False)
        head = h[:h.find("</head>")]
        script = SCRIPT_ADSENSE in head
        con_script += script
        noindex = '<meta name="robots" content="noindex' in head
        privacy = rel == "privacy.html" or rel.endswith("privacy/index.html")
        if SCRIPT_ADSENSE in h[h.find("</head>"):]:
            err.append(f"{rel}: script AdSense fuori dal <head>")
        if privacy:
            if script:
                err.append(f"{rel}: script AdSense in una pagina privacy")
            continue
        if proprie < SOGLIA_PAROLE_PROPRIE:
            if script:
                err.append(f"{rel}: script AdSense con {proprie} parole proprie (soglia {SOGLIA_PAROLE_PROPRIE})")
            if not noindex and rel != "404.html":
                if re.search(r'<a\b[^>]*\brel="[^"]*\bsponsored\b', h) or "di affiliazione" in unescape(re.sub(r"<[^>]+>", " ", m_main(h))):
                    err.append(f"{rel}: link di affiliazione o riga di trasparenza in una pagina sotto la soglia")
                sotto[rel] = proprie
        elif not script and not noindex and len(re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", m_main(h), flags=re.S))))) >= 400:
            err.append(f"{rel}: {proprie} parole proprie e testo sufficiente, ma senza script AdSense")
    if SCRIPT_ADSENSE not in (SITO / "index.html").read_text(encoding="utf-8").split("</head>")[0]:
        err.append("index.html: la home non ha lo script AdSense")
    C = json.loads((SITO.parent / "dati" / "cancello_pubblicita.json").read_text(encoding="utf-8"))
    if SOGLIA_PAROLE_PROPRIE < 100 or C["soglia_parole_proprie"] != SOGLIA_PAROLE_PROPRIE:
        err.append("cancello della pubblicità: soglia sotto 100 o diversa tra verifica.py e dati/cancello_pubblicita.json")
    diverse = sorted((k, v, sotto.get(k)) for k, v in C["pagine"].items() if sotto.get(k) != v)
    if diverse:
        err.append(f"cancello della pubblicità: misura rifatta diversa da dati/cancello_pubblicita.json (pagina, là, qui): {diverse[:5]}")
    return con_script, len(sotto)


def m_main(h):
    m = re.search(r"<main[^>]*>(.*?)</main>", h, re.S)
    return m.group(1) if m else ""


def main():
    err = []
    pagine = sorted(SITO.rglob("*.html"))
    ids = {f: set(re.findall(r'\sid="([^"]+)"', f.read_text(encoding="utf-8"))) for f in pagine}
    # sitemap.xml è un indice (25/11/2026): le pagine stanno nelle sitemap di sezione elencate; lastmod vero da dati/lastmod.json
    indice = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    file_sm = [u.rsplit("/", 1)[1] for u in re.findall(r"<loc>([^<]+)</loc>", indice)]
    if "<sitemapindex" not in indice or not file_sm:
        err.append("sitemap.xml: non è un indice di sitemap")
    voci = []
    for nome in file_sm:
        if nome == "sitemap-vecchi-indirizzi.xml" or not (SITO / nome).exists():
            err.append(f"sitemap.xml: {nome} non deve stare nell'indice o non esiste")
            continue
        voci += re.findall(r"<url><loc>([^<]+)</loc><lastmod>([^<]+)</lastmod></url>", (SITO / nome).read_text(encoding="utf-8"))
    sitemap = {u for u, _ in voci}
    if len(voci) != len(sitemap):
        err.append("sitemap: un indirizzo compare in più di una sitemap di sezione")
    registro = json.loads((SITO.parent / "dati" / "lastmod.json").read_text(encoding="utf-8"))["pagine"]
    for u, giorno in voci:
        if registro.get(u[len(URL):], [None])[0] != giorno or not re.fullmatch(r"20\d\d-\d\d-\d\d", giorno):
            err.append(f"sitemap: lastmod di {u} diverso dal registro dati/lastmod.json")
    robots = (SITO / "robots.txt").read_text(encoding="utf-8")
    if robots.count("Sitemap:") != 1 or f"Sitemap: {URL}sitemap.xml" not in robots:
        err.append("robots.txt: deve indicare solo sitemap.xml")
    vecchi = re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap-vecchi-indirizzi.xml").read_text(encoding="utf-8"))
    for u in vecchi:  # vecchio host, e la pagina di oggi esiste allo stesso percorso (301 dal vecchio indirizzo, poi 200)
        perc = u[len("https://esameb1.netlify.app/"):]
        if not u.startswith("https://esameb1.netlify.app/") or not (SITO / (perc if perc.endswith(".html") else perc + "index.html")).is_file():
            err.append(f"sitemap-vecchi-indirizzi.xml: {u} non è un vecchio indirizzo con la pagina di oggi")
    if not vecchi:
        err.append("sitemap-vecchi-indirizzi.xml: vuota")
    # la home non linka pagine in noindex (25/11/2026)
    home = (SITO / "index.html").read_text(encoding="utf-8")
    for href in set(re.findall(r'<a [^>]*href="([^"#:]+/)"', home)):
        dest = SITO / href / "index.html"
        if dest.exists() and '<meta name="robots" content="noindex' in dest.read_text(encoding="utf-8"):
            err.append(f"index.html: link a una pagina in noindex: {href}")
    for f in pagine:
        if "<!--piu-usate:" in f.read_text(encoding="utf-8"):
            err.append(f"{f.relative_to(SITO)}: segnaposto «più usate» non riempito")
    n_link = n_faq = 0
    tit, des = collections.defaultdict(list), collections.defaultdict(list)
    for f in pagine:
        h = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(SITO))
        head = h[:h.find("</head>")]
        for v in VERIFICHE:
            if v not in head:
                err.append(f"{rel}: manca la verifica di Search Console")
        m = re.search(r'<link rel="canonical" href="([^"]+)"', head)
        canon = URL + rel.replace("index.html", "")
        if not m or m.group(1) != canon:
            err.append(f"{rel}: canonical {m.group(1) if m else 'assente'}")
        noindex = '<meta name="robots" content="noindex' in head
        if f.name != "404.html" and noindex == (canon in sitemap):
            err.append(f"{rel}: sitemap e noindex incoerenti")
        if noindex and "adsbygoogle" in head:
            err.append(f"{rel}: AdSense in una pagina noindex")
        if h.count("<h1") != 1:
            err.append(f"{rel}: {h.count('<h1')} h1")
        visibile = testo(h)
        visibile_compatto = re.sub(r"\s+", "", visibile)  # i tag in mezzo alle frasi (link, grassetti) lasciano spazi in più
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                ld = json.loads(blocco)
            except ValueError:
                err.append(f"{rel}: JSON-LD non valido")
                continue
            grafo = ld.get("@graph", [ld]) if isinstance(ld, dict) else ld
            for nodo in grafo:
                if isinstance(nodo, dict) and nodo.get("@type") == "FAQPage":
                    for q in nodo["mainEntity"]:
                        n_faq += 1
                        for parte in (q["name"], q["acceptedAnswer"]["text"]):
                            if re.sub(r"\s+", "", parte) not in visibile_compatto:
                                err.append(f"{rel}: FAQ non visibile: {parte[:70]}")
        for parola in VIETATE:
            if parola in visibile:
                err.append(f"{rel}: parola «{parola.strip()}» nel testo")
        for href in re.findall(r'href="([^"]+)"', h):
            if href.startswith(("http:", "https:", "mailto:", "tel:", "data:")):
                continue
            n_link += 1
            u = urlparse(unescape(href))
            path = unquote(u.path)
            t = f if not path else ((SITO / path.lstrip("/")) if path.startswith("/") else (f.parent / path)).resolve()
            if path and (path.endswith("/") or t.is_dir()):
                t = t / "index.html"
            if not t.exists():
                if not (SITO / "netlify.toml").read_text(encoding="utf-8").count(f'from = "{path.rstrip("/")}'):
                    err.append(f"{rel}: link rotto {href}")
                continue
            if u.fragment and t.suffix == ".html" and u.fragment not in ids.get(t, set()):
                err.append(f"{rel}: ancora rotta {href}")
        if not noindex and f.name != "404.html":
            t_ = unescape(re.search(r"<title>(.*?)</title>", head, re.S).group(1))
            md = re.search(r'<meta name="description" content="([^"]*)"', head)
            d_ = unescape(md.group(1)) if md else ""
            tit[t_].append(rel)
            des[d_].append(rel)
            if len(t_) > 65 or not d_ or len(d_) > 155:
                err.append(f"{rel}: titolo {len(t_)} o description {len(d_)} fuori limite")
    doppi_t = {k: v for k, v in tit.items() if len(v) > 1 and k != "Privacy | EsameB1"}  # privacy it/en: stesso titolo, già noto
    doppi_d = {k: v for k, v in des.items() if len(v) > 1}
    for k, v in doppi_t.items():
        err.append(f"titolo doppio «{k}»: {v}")
    for k, v in doppi_d.items():
        err.append(f"description doppia «{k[:60]}»: {v}")
    n_cpia = controlli_cpia(err)
    con_script, sotto = controlli_cancello(err)
    print(f"cancello della pubblicità (misura rifatta qui, soglia {SOGLIA_PAROLE_PROPRIE} parole proprie): script AdSense su {con_script} pagine, "
          f"{sotto} pagine in indice sotto la soglia senza script e senza link di affiliazione, privacy senza script, home con lo script")
    print(f"pagine CPIA controllate contro i dati: {n_cpia}")
    print(f"pagine {len(pagine)}, in sitemap {len(sitemap)}, link interni {n_link}, domande FAQ {n_faq}, errori {len(err)}")
    for e in err[:60]:
        print("ERRORE:", e)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
