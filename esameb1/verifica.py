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
    print(f"pagine {len(pagine)}, in sitemap {len(sitemap)}, link interni {n_link}, domande FAQ {n_faq}, errori {len(err)}")
    for e in err[:60]:
        print("ERRORE:", e)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
