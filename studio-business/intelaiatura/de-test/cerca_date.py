"""Per ogni sede delle 20 città cerca la pagina del test e conta le date future leggibili.

Regole: user-agent di un browser normale, robots.txt rispettato, al massimo ~12 pagine per sede,
una richiesta alla volta per sito con una pausa, nessun aggiramento di blocchi (403/anti-robot = "bloccato").

Passi per ogni sede:
 1. robots.txt del sito;
 2. pagina di partenza (sito della sede);
 3. link interni il cui indirizzo o testo parla di Einbürgerungstest / Leben in Deutschland / DTZ / Prüfung,
    in ordine di pertinenza, poi un secondo livello di link dalle pagine pertinenti;
 4. in ogni pagina HTML: date future (31/10/2026 - 31/12/2027) a meno di 250 caratteri da una parola chiave
    (einbürgerung, leben in deutschland, LiD, DTZ, Deutsch-Test für Zuwanderer).
I PDF trovati si contano a parte (non sono "HTML leggibile").
Scrive grezzi/date/<n>.json per sede e grezzi/date_risultati.json.
Uso: python3 -I cerca_date.py [indice_iniziale indice_finale]
"""
import concurrent.futures as cf
import datetime as dt
import html
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.robotparser

import requests

QUI = pathlib.Path(__file__).resolve().parent
OUT = QUI / "grezzi" / "date"
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
OGGI = dt.date(2026, 10, 30)
FINE = dt.date(2027, 12, 31)
MAX_PAGINE = 20

MESI = {"januar": 1, "jänner": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4, "mai": 5, "juni": 6,
        "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,
        "jan": 1, "feb": 2, "mär": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
        "okt": 10, "nov": 11, "dez": 12}
RE_NUM = re.compile(r"(?<![\d.])(\d{1,2})\.\s?(\d{1,2})\.\s?(20\d\d|\d\d)(?!\d)")
RE_MESE = re.compile(r"(?<!\d)(\d{1,2})\.\s*(" + "|".join(sorted(MESI, key=len, reverse=True)) + r")\.?\s+(20\d\d)", re.I)
RE_CHIAVE = re.compile(r"einbürgerung|einbuergerung|leben in deutschland|\blid\b|\bdtz\b|deutsch-test für zuwanderer", re.I)
RE_LINK_FORTE = re.compile(r"einb(ü|ue|u)rger|leben-in-deutschland|lebenindeutschland|\blid\b|lid-test|dtz|deutsch-test", re.I)
RE_LINK_DEBOLE = re.compile(r"pr(ü|ue)fung|test|deutsch.*(zweit|fremd|integration)|integration|daz|sprachkurs|termine", re.I)


class Sito:
    def __init__(self, base):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "de-DE,de;q=0.9"})
        self.robots = {}

    def permesso(self, url):
        p = urllib.parse.urlparse(url)
        host = p.scheme + "://" + p.netloc
        if host not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.s.get(host + "/robots.txt", timeout=15)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except Exception:
                rp.parse([])
            self.robots[host] = rp
        return self.robots[host].can_fetch(UA, url)

    def prendi(self, url):
        if not self.permesso(url):
            return {"url": url, "stato": "robots"}
        time.sleep(0.7)
        try:
            r = self.s.get(url, timeout=25, allow_redirects=True)
        except Exception as e:
            return {"url": url, "stato": "errore", "err": type(e).__name__}
        tipo = r.headers.get("content-type", "")
        return {"url": r.url, "stato": r.status_code, "tipo": tipo, "corpo": r.content}


def testo(html_bytes):
    t = html_bytes.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|td|th|h\d)>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"[ \t\xa0]+", " ", t)


def link(html_bytes, base):
    t = html_bytes.decode("utf-8", "replace")
    out = []
    for m in re.finditer(r'(?is)<a\b[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', t):
        href = html.unescape(m.group(1)).strip()
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        u = urllib.parse.urljoin(base, href)
        ancora = html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
        out.append((u, " ".join(ancora.split())))
    return out


def date_future(t):
    trovate = []
    for m in list(RE_NUM.finditer(t)) + list(RE_MESE.finditer(t)):
        try:
            g = int(m.group(1))
            mese = int(m.group(2)) if m.re is RE_NUM else MESI[m.group(2).lower().rstrip(".")]
            a = int(m.group(3))
            a = a + 2000 if a < 100 else a
            d = dt.date(a, mese, g)
        except Exception:
            continue
        if not (OGGI < d <= FINE):
            continue
        ctx = t[max(0, m.start() - 250): m.end() + 250]
        if RE_CHIAVE.search(ctx):
            trovate.append({"data": d.isoformat()})  # il testo intorno non si salva: può contenere nomi
    return trovate


def stesso_sito(u, basi):
    """u è dello stesso sito di una delle basi? Per berlin.de vale solo la sezione della singola VHS."""
    pu = urllib.parse.urlparse(u)
    a = pu.netloc.lower().removeprefix("www.")
    for base in basi:
        pb = urllib.parse.urlparse(base)
        b = pb.netloc.lower().removeprefix("www.")
        if b == "berlin.de":
            if a == "berlin.de" and pu.path.startswith(pb.path):
                return True
            continue
        if a == b or a.endswith("." + b) or b.endswith("." + a):
            return True
    return False


def chiave_url(u):
    return u.split("?")[0].rstrip("/").lower()


def esplora(sede):
    url0 = sede["url_partenza"]
    rapporto = {"nome": sede["nome"], "citta": sede["citta"], "url_partenza": url0,
                "pagine": [], "pdf": [], "date": [], "esito": ""}
    if not url0:
        rapporto["esito"] = "senza sito"
        return rapporto
    sito = Sito(url0)
    basi = [url0] + sede.get("url_extra", [])
    visti, coda = set(), [(0, url0)] + [(0, u) for u in sede.get("url_extra", [])]
    while coda and len(rapporto["pagine"]) < MAX_PAGINE:
        coda.sort(key=lambda x: x[0])
        _, u = coda.pop(0)
        if chiave_url(u) in visti:
            continue
        visti.add(chiave_url(u))
        r = sito.prendi(u)
        if r.get("url") and len(rapporto["pagine"]) == 0 and r["url"] != u:
            basi.append(r["url"])  # il sito di partenza ha rediretto su un altro dominio
        voce = {"url": r["url"], "stato": r["stato"]}
        rapporto["pagine"].append(voce)
        if r["stato"] != 200:
            continue
        if "pdf" in r.get("tipo", "") or r["url"].lower().endswith(".pdf"):
            rapporto["pdf"].append(r["url"])
            continue
        if "html" not in r.get("tipo", ""):
            continue
        corpo = r["corpo"]
        t = testo(corpo)
        voce["chiave"] = bool(RE_CHIAVE.search(t))
        voce["byte"] = len(corpo)
        df = date_future(t)
        if df:
            voce["n_date"] = len(df)
            for d in df:
                d["pagina"] = r["url"]
            rapporto["date"].extend(df)
        for lu, anc in link(corpo, r["url"]):
            if chiave_url(lu) in visti:
                continue
            if lu.lower().endswith(".pdf"):
                if RE_LINK_FORTE.search(lu) or RE_LINK_FORTE.search(anc):
                    rapporto["pdf"].append(lu)
                continue
            if not stesso_sito(lu, basi):
                continue
            if RE_LINK_FORTE.search(lu) or RE_LINK_FORTE.search(anc):
                coda.append((1, lu))
            elif voce["chiave"] is False and len(rapporto["pagine"]) <= 2 and RE_LINK_DEBOLE.search(lu + " " + anc):
                coda.append((3, lu))
    stati = [p["stato"] for p in rapporto["pagine"]]
    if rapporto["date"]:
        rapporto["esito"] = "date future in HTML"
    elif stati and all(s in (403, 429, 503, "robots") for s in stati[:1]):
        rapporto["esito"] = "bloccato (" + str(stati[0]) + ")"
    elif stati and stati[0] != 200:
        rapporto["esito"] = "sito non raggiungibile (" + str(stati[0]) + ")"
    elif rapporto["pdf"]:
        rapporto["esito"] = "solo PDF"
    elif any(p.get("chiave") for p in rapporto["pagine"]):
        rapporto["esito"] = "pagina del test senza date future"
    else:
        rapporto["esito"] = "pagina del test non trovata"
    rapporto["date"] = sorted({d["data"]: d for d in rapporto["date"]}.values(), key=lambda d: d["data"])
    return rapporto


def main():
    sedi = json.loads((QUI / "grezzi" / "sedi_top20.json").read_text())
    a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, len(sedi))
    lavori = list(enumerate(sedi))[a:b]
    with cf.ThreadPoolExecutor(8) as ex:
        fut = {ex.submit(esplora, s): i for i, s in lavori}
        for f in cf.as_completed(fut):
            i = fut[f]
            try:
                r = f.result()
            except Exception as e:
                r = {"nome": sedi[i]["nome"], "citta": sedi[i]["citta"], "esito": "errore script " + repr(e)}
            (OUT / f"{i:03d}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
            print(f"{i:03d} {r['citta']:<11} {r['nome'][:45]:<45} {r['esito']} ({len(r.get('date', []))} date)", flush=True)
    tutti = [json.loads(p.read_text()) for p in sorted(OUT.glob("*.json"))]
    (QUI / "grezzi" / "date_risultati.json").write_text(json.dumps(tutti, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
