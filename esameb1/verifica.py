"""Controllo del sito generato di EsameB1 (esameb1/sito/), da lanciare dopo python3 esameb1/genera.py.

Uso (dalla radice del repository):
    python3 esameb1/verifica.py        # stampa il riepilogo; esce con 1 se c'è almeno un errore

Controlla, su tutte le pagine HTML:
- meta di verifica di Search Console (entrambe le proprietà), canonical giusto, un solo h1;
- sitemap e noindex coerenti (una pagina noindex non è in sitemap, una pagina in indice sì; la 404 è esclusa);
- AdSense mai nelle pagine noindex;
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
            if s["codice"] not in t or s["cap"] not in t:
                err.append(f"{rel}: sede {s['codice']} dell'anagrafe non in pagina")
        if "dati.istruzione.it" not in corpo or f"letta il {letta}" not in t:
            err.append(f"{rel}: manca la fonte del Ministero con la data di lettura")
        citate = {re.sub(r"\s+", " ", x["testo"]) for voci in c["citazioni"].values() for x in voci} | {c["nome_anagrafe"], "Centro territoriale"}
        for frase in re.findall(r"«([^»]+)»", t):
            if frase.strip() not in citate:
                err.append(f"{rel}: testo tra virgolette non citato nei dati: {frase[:60]}")
        for x in citate - {"Centro territoriale"}:
            if x not in t:
                err.append(f"{rel}: frase dei dati non in pagina: {x[:60]}")
        libro = re.findall(r'<a [^>]*data-libro-proprio="si"[^>]*>', corpo)
        if not libro or any('data-goatcounter-click="esameb1.eu/clic/libro-cpia"' not in x for x in libro):
            err.append(f"{rel}: riquadro del libro assente o con un'altra etichetta")
        if "sponsored" in corpo:
            err.append(f"{rel}: link sponsorizzato in una pagina CPIA")
    return len(attese & trovate)


def main():
    err = []
    pagine = sorted(SITO.rglob("*.html"))
    ids = {f: set(re.findall(r'\sid="([^"]+)"', f.read_text(encoding="utf-8"))) for f in pagine}
    sitemap = set(re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8")))
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
    print(f"pagine CPIA controllate contro i dati: {n_cpia}")
    print(f"pagine {len(pagine)}, in sitemap {len(sitemap)}, link interni {n_link}, domande FAQ {n_faq}, errori {len(err)}")
    for e in err[:60]:
        print("ERRORE:", e)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
