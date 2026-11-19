"""Compagnie aeree per cani a confronto (sezione "dog-airlines/", dal 18/11/2026): BARK Air, RetrievAir, K9 Jets. Rilegge i siti ufficiali.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/cani_volo.py            rilegge le fonti, controlla le frasi citate, legge voli e città, scrive dati/cani_volo.json
    python3 -I beforeyoufly/raccolta/cani_volo.py --cache    come sopra ma senza rete, dalle copie in raccolta/.cache/cani_volo/
    python3 -I beforeyoufly/raccolta/cani_volo.py --testo ID stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (18/11/2026, piano: studio-business/intelaiatura/fronti-2026-11-18-animali.md, idea A):
  - Solo le pagine ufficiali di ogni compagnia, lette dal server con HTTP 200: air.bark.co (BARK Air; barkair.com è un dominio parcheggiato,
    non il sito ufficiale) e retrievair.com. Nessun sito di terzi, nessun prezzo di terzi.
  - I fatti sono scritti a mano in dati/cani_volo_manuali.json: ogni frase tra virgolette sul sito è una citazione parola per parola. Se una
    fonte non risponde 200 o una citazione non è più nel testo normalizzato, lo script NON sovrascrive dati/cani_volo.json ed esce con 1.
  - Prezzi di BARK Air: il sito li pubblica volo per volo nel catalogo dei voli (https://air.bark.co/collections/bookings, la stessa lista in
    JSON all'indirizzo .../products.json). Si copiano rotta, numero dei voli in vendita e prezzo minimo e massimo per biglietto, con la data di
    lettura; la valuta si legge dalla pagina (USD). I voli non hanno l'anno nel titolo: non si pubblicano le date dei singoli voli.
  - RetrievAir: nessuna tariffa sulle pagine lette (tariffe dinamiche): si citano solo le penali scritte. Città dal menu del sito, rotte dalle
    pagine /routes/ della sitemap ufficiale (titolo "Pet-Friendly Flights from X to Y").
  - K9 Jets: www.k9jets.com risponde HTTP 403 al server (anche con il browser senza trucchi). Non si aggira: si registra il codice HTTP e la
    data; la pagina del sito dice che non si è potuto leggere. Quando risponderà 200 lo script lo segnala: allora si scrivono le citazioni.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte: se cambia, il cambio va in dati/cani_volo_cambi.json.
  - Pagine grezze in raccolta/.cache/cani_volo/ (escluse da git).
"""
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "cani_volo"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BARK = "https://air.bark.co/"
RV = "https://retrievair.com/"
BARK_VOLI_JSON = BARK + "collections/bookings/products.json?limit=250&page={n}"
RV_ROTTE_SITEMAP = RV + "routes-sitemap.xml"
K9 = "https://www.k9jets.com/"

# id -> pagina ufficiale letta (e linkata dal sito), compagnia, ente, titolo
FONTI = {
    "bk_faq": {"url": BARK + "pages/faq", "c": "bark", "ente": "BARK Air", "titolo": "BARK Air: Frequently Asked Questions"},
    "bk_voli": {"url": BARK + "collections/bookings", "c": "bark", "ente": "BARK Air", "titolo": "BARK Air: Our Routes (flights on sale)"},
    "bk_exp": {"url": BARK + "pages/experience", "c": "bark", "ente": "BARK Air", "titolo": "BARK Air: Fly with us"},
    "bk_charter": {"url": BARK + "pages/charters", "c": "bark", "ente": "BARK Air", "titolo": "BARK Air: Private Charters"},
    "rv_faq": {"url": RV + "faqs/", "c": "retrievair", "ente": "RetrievAir", "titolo": "RetrievAir: FAQs"},
    "rv_how": {"url": RV + "how-it-works/", "c": "retrievair", "ente": "RetrievAir", "titolo": "RetrievAir: How It Works"},
    "rv_dest": {"url": RV + "destinations/", "c": "retrievair", "ente": "RetrievAir", "titolo": "RetrievAir: Routes & Destinations"},
}


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/json,application/xml"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read().decode("utf-8", "replace")


def leggi_stato(url):
    """Solo il codice HTTP (per K9 Jets, che rifiuta il server): nessun tentativo di aggirare."""
    try:
        return leggi(url)[0]
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def testo_html(html_):
    """Testo visibile normalizzato (stesso metodo di raccolta/animali.py), più gli indirizzi email protetti resi uguali ogni volta."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->|<svg.*?</svg>", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ").replace("​", "").replace("⁣", "").replace("﻿", "")
    t = re.sub(r"\s+", " ", t)
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def frasi_fonte(M, fid):
    return [c["x"] for C in M["compagnie"] for c in C.get("citazioni", []) if c["f"] == fid]


def impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:16]


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    return impronta(testo[min(i for i, _ in pos):max(i + n for i, n in pos)])


def valuta_bark(raw):
    m = re.search(r'Shopify\.currency = \{"active":"([A-Z]{3})"', raw)
    return m.group(1) if m else None


def voli_bark(pagine_json):
    """Catalogo dei voli di BARK Air (lista ufficiale in JSON): per rotta, voli in elenco, voli prenotabili, prezzo minimo e massimo del biglietto."""
    rotte = {}
    for raw in pagine_json:
        for p in json.loads(raw)["products"]:
            if p.get("product_type") != "Flight" or "|" not in p["title"]:
                continue
            nome = re.sub(r"\s+", " ", p["title"].split("|")[0]).strip()
            m = re.fullmatch(r"(.+?) To (.+)", nome)
            if not m:
                continue
            r = rotte.setdefault(nome, {"da": m.group(1), "a": m.group(2), "voli": 0, "prenotabili": 0, "prezzi": []})
            r["voli"] += 1
            v = p["variants"][0]
            r["prenotabili"] += 1 if v.get("available") else 0
            r["prezzi"].append(float(v["price"]))
    out = []
    for nome in sorted(rotte):
        r = rotte[nome]
        out.append({"da": r["da"], "a": r["a"], "voli": r["voli"], "prenotabili": r["prenotabili"], "min": min(r["prezzi"]), "max": max(r["prezzi"])})
    return out


def citta_rv(raw):
    """Città servite: le voci del menu 'Destinations' del sito (link /cities/<slug>/ con il nome)."""
    out = []
    for slug, nome in re.findall(r'<a class="wp-block-navigation-item__content"\s+href="https://retrievair\.com/cities/([a-z0-9-]+)/"[^>]*>(.*?)</a>', raw, re.S):
        nome = testo_html(nome)
        if nome and nome not in [x["nome"] for x in out]:
            out.append({"nome": nome, "url": f"{RV}cities/{slug}/"})
    return out


def rotte_rv(sitemap, leggi_pagina):
    """Pagine /routes/ della sitemap ufficiale: da e a dal titolo della pagina ('Pet-Friendly Flights from X to Y')."""
    out = []
    for u in re.findall(r"<loc>(https://retrievair\.com/routes/[a-z0-9-]+/)</loc>", sitemap):
        raw = leggi_pagina(u)
        m = re.search(r"<h1[^>]*>(.*?)</h1>", raw or "", re.S)
        t = testo_html(m.group(1)) if m else ""
        mm = re.fullmatch(r"Pet-Friendly Flights from (.+?) to (.+)", t)
        if mm:
            out.append({"da": mm.group(1), "a": mm.group(2), "url": u})
    return sorted(out, key=lambda r: (r["da"], r["a"]))


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "cani_volo_manuali.json").read_text(encoding="utf-8"))
    f_dati = DATI / "cani_volo.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    problemi, letture, cambi, grezzi = [], {}, [], {}

    def prendi(nome, url, tentativi=3):
        """Testo grezzo di un indirizzo (rete o copia salvata) e codice HTTP; None se non si legge."""
        f = CACHE / nome
        if da_cache:
            return (f.read_text(encoding="utf-8"), 200) if f.exists() else (None, 0)
        errore = None
        for k in range(tentativi):
            try:
                stato, _, raw = leggi(url)
                if stato == 200:
                    f.write_text(raw, encoding="utf-8")
                return raw, stato
            except urllib.error.HTTPError as e:
                return None, e.code
            except Exception as e:  # rete: si riprova
                errore = e
                time.sleep(4 + 6 * k)
        print(f"  {url}: lettura fallita ({errore})")
        return None, 0

    for fid, F in FONTI.items():
        P = prima["fonti"].get(fid) or {}
        raw, stato = prendi(f"{fid}.html", F["url"])
        if raw is None or stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
            continue
        grezzi[fid] = raw
        t = testo_html(raw)
        frasi = frasi_fonte(M, fid)
        for x in frasi:
            if x not in t:
                problemi.append(f"{fid}: frase non trovata: {x[:90]!r}")
        letto = oggi if not da_cache else (P.get("letto_il") or oggi)
        letture[fid] = {"url": F["url"], "pagina": F["url"], "c": F["c"], "http": stato, "byte": len(raw.encode("utf-8")), "ente": F["ente"], "titolo": F["titolo"],
                        "letto_il": letto, "impronta": impronta_zona(t, frasi) if frasi else None, "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {letture[fid]['byte']} byte, {len(frasi)} frasi, impronta {letture[fid]['impronta']}")
        if P.get("impronta") and letture[fid]["impronta"] and P["impronta"] != letture[fid]["impronta"]:
            cambi.append({"data": oggi, "fonte": fid, "cosa": "zona citata", "prima": P["impronta"], "dopo": letture[fid]["impronta"]})
            print(f"  CAMBIATA la zona citata di {fid}: rileggere la pagina")
        time.sleep(1)
    # BARK Air: voli in vendita e prezzi (catalogo ufficiale)
    pagine_json = []
    for n in range(1, 6):
        raw, stato = prendi(f"bk_voli_{n}.json", BARK_VOLI_JSON.format(n=n))
        if raw is None or stato != 200:
            if n == 1:
                problemi.append(f"catalogo dei voli di BARK Air: HTTP {stato}")
            break
        if not json.loads(raw).get("products"):
            break
        pagine_json.append(raw)
        time.sleep(1)
    voli = voli_bark(pagine_json)
    valuta = valuta_bark(grezzi.get("bk_voli", ""))
    if len(voli) < 4:
        problemi.append(f"catalogo dei voli di BARK Air: solo {len(voli)} rotte lette")
    if valuta != "USD":
        problemi.append(f"BARK Air: valuta della pagina dei voli non letta o diversa da USD ({valuta})")
    # RetrievAir: città e rotte
    citta = citta_rv(grezzi.get("rv_dest", ""))
    sm, stato_sm = prendi("rv_rotte_sitemap.xml", RV_ROTTE_SITEMAP)

    def pagina_rotta(u):
        raw, st = prendi("rv_rotta_" + u.rstrip("/").rsplit("/", 1)[-1] + ".html", u)
        time.sleep(0.5)
        return raw if st == 200 else ""

    rotte = rotte_rv(sm or "", pagina_rotta)
    if len(citta) < 4:
        problemi.append(f"RetrievAir: solo {len(citta)} città lette dal menu")
    if stato_sm != 200 or not rotte:
        problemi.append(f"RetrievAir: sitemap delle rotte HTTP {stato_sm}, {len(rotte)} rotte lette")
    # K9 Jets: solo il codice HTTP
    Pk = (prima.get("non_lette") or {}).get("k9") or {}
    http_k9 = Pk.get("http", 403) if da_cache else leggi_stato(K9)
    print(f"  K9 Jets: HTTP {http_k9}" + (" — ORA RISPONDE: leggere le pagine e scrivere le citazioni in dati/cani_volo_manuali.json" if http_k9 == 200 else ""))
    if problemi:
        print("NON SCRITTO dati/cani_volo.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    doc = {"_nota": "Compagnie aeree per cani: citazioni scritte a mano in dati/cani_volo_manuali.json, fonti rilette da raccolta/cani_volo.py (HTTP, data di "
                    "lettura, impronta della zona citata); voli e prezzi di BARK Air dal catalogo ufficiale del suo sito; città e rotte di RetrievAir "
                    "dal suo sito. Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture,
           "bark_voli": {"url": BARK + "collections/bookings", "valuta": valuta, "letto_il": letture["bk_voli"]["letto_il"], "rotte": voli,
                         "impronta": impronta(json.dumps(voli, sort_keys=True))},
           "rv": {"citta": citta, "rotte": rotte, "sitemap": RV_ROTTE_SITEMAP, "letto_il": letture["rv_dest"]["letto_il"]},
           "non_lette": {"k9": {"url": K9, "http": http_k9, "letto_il": oggi if not da_cache else Pk.get("letto_il", oggi)}},
           "righe": M["righe"], "compagnie": M["compagnie"], "faq_indice": M["faq_indice"]}
    Pv = prima.get("bark_voli") or {}
    if Pv.get("impronta") and Pv["impronta"] != doc["bark_voli"]["impronta"]:
        cambi.append({"data": oggi, "fonte": "bk_voli", "cosa": "voli e prezzi", "prima": Pv["impronta"], "dopo": doc["bark_voli"]["impronta"]})
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "cani_volo_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(letture)} fonti, BARK Air {len(voli)} rotte e {sum(r['voli'] for r in voli)} voli in elenco, "
          f"RetrievAir {len(citta)} città e {len(rotte)} pagine rotta, K9 Jets HTTP {http_k9}" + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        f_cache = CACHE / f"{fid}.html"
        if not f_cache.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_cache.write_text(leggi(FONTI[fid]["url"])[2], encoding="utf-8")
        print(testo_html(f_cache.read_text(encoding="utf-8")))
        sys.exit(0)
    main()
