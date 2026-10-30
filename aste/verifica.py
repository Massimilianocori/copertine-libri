"""Controlli prima di pubblicare Aste in Chiaro.

Uso (dalla radice del repository, dopo python3 aste/genera.py):
    python3 aste/verifica.py            # controlli statici
    python3 aste/verifica.py --browser  # anche Playwright (390 e 1280 px, tema chiaro e scuro)

1. Ogni link interno (href/src) punta a un file esistente in sito/.
2. Sitemap: ogni URL esiste, ogni pagina con canonical è nella sitemap; robots.txt la cita.
3. Ogni pagina HTML: meta di verifica Google, un solo <h1>, <title> e meta description.
4. Dati personali: nessuna email, nessun codice fiscale, nessun numero di telefono, nessun campo personale del PVP
   (soggetti, nome/cognome, email, codici fiscali, allegati) né nelle pagine né in dati/ né nella cache dei dettagli.
5. OMI: ogni pagina con un valore €/m² cita «Agenzia delle Entrate – OMI» e il semestre; ogni scheda con lo sconto ha il semestre.
6. Ogni lotto (scheda o riga) ha il link alla sua scheda ufficiale sul PVP.
7. Nessuna data oltre il 2030; nessuna scheda con €/m² senza superficie.
8. La parola «affare»/«occasione» non compare come giudizio (ammessa solo nella pagina Metodo, dove diciamo che non la usiamo).
9. Il riquadro mutuo non compare finché dati/affiliati.json non ha l'URL.
10. Nessun nome di modelli o servizi di intelligenza artificiale nei file del progetto (cache esclusa).
11. live.json: formato giusto e contiene ogni lotto pubblicato.
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
Esce con codice 1 se qualcosa non va.
"""
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402

RADICE = G.RADICE
SITO = G.SITO
DATI = G.DATI
ERR = []


def errore(msg):
    ERR.append(msg)


class Analisi(HTMLParser):
    def __init__(self):
        super().__init__()
        self.link, self.h1, self.title, self.descr, self.canon, self.verifica, self.svg = [], 0, 0, 0, None, False, 0

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg -= 1

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.link.append(a["href"])
        if tag in ("img", "script") and a.get("src"):
            self.link.append(a["src"])
        if tag == "link" and a.get("rel") in ("preload", "stylesheet", "icon"):
            self.link.append(a.get("href"))
        if tag == "use" and a.get("href"):
            self.link.append(a["href"].split("#")[0])
        if tag == "h1":
            self.h1 += 1
        if tag == "svg":
            self.svg += 1
        if tag == "title" and not self.svg:
            self.title += 1
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.descr += 1
        if tag == "meta" and a.get("name") == "google-site-verification" and a.get("content") == G.GOOGLE_VERIFICA:
            self.verifica = True
        if tag == "link" and a.get("rel") == "canonical":
            self.canon = a.get("href")


def risolvi(pagina, href):
    if not href or href.startswith(("http://", "https://", "mailto:", "data:", "#", "javascript:")):
        return None
    p = unquote(urlparse(href).path)
    if not p:
        return None
    base = SITO if p.startswith("/") else pagina.parent
    t = (base / p.lstrip("/")).resolve()
    if p.endswith("/"):
        t = t / "index.html"
    return t


RX_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RX_CF = re.compile(r"\b[A-Z]{6}\d{2}[A-EHLMPR-T]\d{2}[A-Z]\d{3}[A-Z]\b", re.I)
RX_TEL = re.compile(r"(?<![\d.,])(?:\+39[ ]?)?3\d{2}[ ]?\d{6,7}(?![\d.,])")
CAMPI_PERSONALI = re.compile(r'"(soggetti|cognome|email|cellulare|telefono|codiceFiscale|codfis\w*|cognomeTitolarePegno|'
                             r'nomeTitolarePegno|allegati|allegatoDTO|datiCatastali|idSoggetto)"\s*:')


def testo_visibile(html):
    html = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def controlla_pagine():
    pagine = sorted(SITO.rglob("*.html"))
    canon = set()
    n_link = 0
    for p in pagine:
        t = p.read_text(encoding="utf-8")
        a = Analisi()
        a.feed(t)
        rel = p.relative_to(SITO).as_posix()
        for href in a.link:
            dest = risolvi(p, href)
            if dest is None:
                continue
            n_link += 1
            if not dest.exists():
                errore(f"{rel}: link rotto {href}")
        if not a.verifica:
            errore(f"{rel}: manca la meta di verifica Google")
        if a.h1 != 1:
            errore(f"{rel}: {a.h1} <h1>")
        if a.title != 1 or a.descr != 1:
            errore(f"{rel}: title {a.title}, description {a.descr}")
        if a.canon:
            canon.add(a.canon)
        vis = testo_visibile(t)
        # 4. dati personali
        for rx, nome in ((RX_EMAIL, "email"), (RX_CF, "codice fiscale"), (RX_TEL, "telefono")):
            m = rx.search(vis) or rx.search(t)
            if m:
                errore(f"{rel}: possibile {nome} nella pagina: {m.group(0)}")
        # 5. OMI: attribuzione e semestre
        if "€/m²" in vis:
            if G.ATTRIB not in vis or (G.SEM_TESTO not in vis and G.SEM_BREVE not in vis):
                errore(f"{rel}: valori €/m² senza «{G.ATTRIB}» o senza semestre")
        for blocco in t.split('<li class="lotto"')[1:]:
            blocco = blocco.split("\n</li>")[0]
            i = re.search(r'data-id="(\d+)"', blocco).group(1)
            if 'class="sc ' in blocco and G.SEM_BREVE not in blocco:
                errore(f"{rel}: lotto {i} con sconto senza semestre OMI")
            if G.PVP_LOTTO.format(i).replace("&", "&amp;") not in blocco and G.PVP_LOTTO.format(i) not in blocco:
                errore(f"{rel}: lotto {i} senza link alla scheda PVP")
            if 'class="sc ' in blocco and not re.search(r"\(\d+ m²\)", blocco):
                errore(f"{rel}: lotto {i} con sconto senza superficie")
        # 6. righe dei veicoli
        for m in re.finditer(r'<tr data-id="(\d+)"(.*?)</tr>', t, flags=re.S):
            if G.PVP_LOTTO.format(m.group(1)) not in m.group(2):
                errore(f"{rel}: veicolo {m.group(1)} senza link al PVP")
        # 7. date
        for d in re.findall(r'data-data="(\d{4})-', t):
            if int(d) > 2030:
                errore(f"{rel}: data oltre il 2030")
        # 8. parole vietate
        if rel != "metodologia/index.html" and re.search(r"\b(affar[ei]|occasion[ei])\b", vis, re.I):
            errore(f"{rel}: compare «affare/occasione»")
        # 9. affiliati
        if not (G.AFFILIATI.get("mutuo") or {}).get("url") and "mutuo-box" in t.replace(".mutuo-box", ""):
            errore(f"{rel}: riquadro mutuo presente senza URL")
    return pagine, canon, n_link


def controlla_sitemap(canon):
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    urls = re.findall(r"<loc>(.*?)</loc>", sm)
    if len(urls) != len(set(urls)):
        errore("sitemap: URL duplicati")
    for u in urls:
        p = u.replace(G.URL_SITO + "/", "")
        f = SITO / (p if p.endswith(".html") else p + "index.html")
        if not f.exists():
            errore(f"sitemap: {u} non esiste")
    for c in canon:
        if c not in urls:
            errore(f"canonical fuori dalla sitemap: {c}")
    if f"Sitemap: {G.URL_SITO}/sitemap.xml" not in (SITO / "robots.txt").read_text():
        errore("robots.txt senza sitemap")
    return urls


def controlla_dati():
    for f in list(DATI.glob("*.json")) + list((RADICE / "cache" / "dettagli").glob("*.json"))[:100000]:
        t = f.read_text(encoding="utf-8")
        if CAMPI_PERSONALI.search(t):
            errore(f"{f.relative_to(RADICE)}: campo personale del PVP")
        if f.parent == DATI:
            for rx, nome in ((RX_EMAIL, "email"), (RX_CF, "codice fiscale")):
                m = rx.search(t)
                if m:
                    errore(f"{f.relative_to(RADICE)}: possibile {nome}: {m.group(0)}")
    live = json.loads((DATI / "live.json").read_text(encoding="utf-8"))
    if not live.get("letto_il") or not isinstance(live.get("lotti"), dict):
        errore("live.json: formato errato")
    pubblicati = {str(L["id"]) for L in G.LOTTI} | {str(v["id"]) for v in G.VEICOLI}
    mancano = [i for i in pubblicati if i not in live["lotti"]]
    if mancano:
        errore(f"live.json: mancano {len(mancano)} lotti pubblicati (es. {mancano[:3]}): rilanciare aggiorna.py prima di genera.py")
    for i, v in list(live["lotti"].items())[:50000]:
        if not (isinstance(v, list) and len(v) == 3 and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d", v[2] or "")):
            errore(f"live.json: voce {i} non valida")
            break


def controlla_parole_ai():
    nomi = ["cl" + "aude", "chat" + "gpt", "gp" + r"t-?\d", "open" + "ai", "anth" + "ropic", "gem" + "ini", "lla" + "ma", "co" + "pilot", "mis" + "tral"]
    rx = re.compile(r"\b(" + "|".join(nomi) + r")\b", re.I)
    for f in RADICE.rglob("*"):
        if f.is_dir() or "cache" in f.parts or f.suffix in (".woff2", ".png", ".pyc") or "__pycache__" in f.parts:
            continue
        try:
            t = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        m = rx.search(t)
        if m:
            errore(f"{f.relative_to(RADICE)}: nome di un servizio di IA ({m.group(0)})")


def controlla_indexnow():
    """File chiave IndexNow in sito/: presente, con dentro solo la chiave, fuori dalla sitemap (scritto da genera.py accanto a robots.txt)."""
    f = SITO / f"{G.CHIAVE_INDEXNOW}.txt"
    if not f.exists():
        errore(f"file chiave IndexNow mancante: {f.name}")
    elif f.read_text(encoding="utf-8").strip() != G.CHIAVE_INDEXNOW:
        errore(f"file chiave IndexNow con contenuto sbagliato: {f.name}")
    if f.name in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
        errore("file chiave IndexNow citato nella sitemap")
    print(f"File chiave IndexNow {f.name}: {'presente' if f.exists() else 'MANCANTE'}.")


def controlla_monetizzazione():
    """Controllo comune di monetizzazione (studio-business/strumenti/monetizzazione.py): link di affiliazione solo verso i domini
    ammessi di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza; AdSense, ads.txt e privacy coerenti."""
    errori, info = G.MON.controlla_sito(G.SITO_ID, SITO)
    for e in errori:
        errore(e)
    print(G.MON.riepilogo(G.SITO_ID, info, errori) + ".")


def main():
    pagine, canon, n_link = controlla_pagine()
    urls = controlla_sitemap(canon)
    controlla_dati()
    controlla_parole_ai()
    print(f"Pagine HTML: {len(pagine)}; link interni controllati: {n_link}; URL in sitemap: {len(urls)}.")
    controlla_indexnow()
    controlla_monetizzazione()
    if "--browser" in sys.argv:
        r = subprocess.run(["node", str(RADICE / "verifica_browser.js")])
        if r.returncode:
            errore("controllo nel browser fallito")
    if ERR:
        print(f"{len(ERR)} PROBLEMI:")
        print("\n".join(ERR[:200]))
        sys.exit(1)
    print("Tutto a posto.")


if __name__ == "__main__":
    main()
