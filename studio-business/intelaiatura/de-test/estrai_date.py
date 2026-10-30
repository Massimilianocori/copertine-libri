"""Estrattore delle date d'esame (Einbürgerungstest / Leben in Deutschland / DTZ) dalle pagine delle sedi.

Ingresso: grezzi/sedi_top20.json + le pagine trovate da cerca_date.py (grezzi/date_passata1, grezzi/date)
          + le pagine trovate a mano (PAGINE_A_MANO qui sotto).
Uscita:   grezzi/estratte.json  (per sede: formato, date d'esame future, tipo, pagina fonte; SENZA il testo
          intorno alle date, perché può contenere nomi di persone)
          e un riepilogo a schermo.
Il testo intorno alle date per i controlli a mano va in un file della cartella temporanea passata come argomento.

Regole:
- legge solo HTML (user-agent di browser, robots.txt rispettato, pausa tra richieste);
- una data conta se è futura (31/10/2026 - 31/12/2027) e la "voce" in cui si trova parla del test:
  parola chiave (Einbürgerung, Leben in Deutschland, LiD, DTZ, Zuwanderer) nei 220 caratteri prima
  (fermandosi alla data precedente se la data precedente è lontana, cioè se non è un elenco di date),
  oppure la pagina è dedicata al test (parola chiave nell'indirizzo o nel titolo) e vicino c'è "Termin/Prüfung/Test";
- scarta le date di corsi (Integrationskurs, Alphabetisierung, Umschulung, Kursstart...) e le marca
  come "scadenza" se precedute da Anmeldeschluss / Anmeldung bis / Meldefrist / Rücktritt, come
  "apertura" se precedute da "Anmeldung ab".
Uso: python3 -I estrai_date.py <cartella_temporanea>
"""
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
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
UA_BERLINO = "PruefstellenTest/0.1 (einmalige Machbarkeitspruefung; robots.txt respektiert)"
OGGI, FINE = dt.date(2026, 10, 30), dt.date(2027, 12, 31)

PAGINE_A_MANO = {  # (città, inizio del nome) -> pagine con le date, trovate seguendo i link a mano
    ("berlin", "VHS Berlin-Tempelhof"): ["https://www.berlin.de/vhs-tempelhof-schoeneberg/"],
    ("berlin", "VHS Berlin-Mitte"): ["https://www.berlin.de/vhs/volkshochschulen/mitte/"],
    ("berlin", "VHS Berlin-Charlottenburg"): ["https://www.berlin.de/vhs/volkshochschulen/charlottenburg-wilmersdorf/"],
    ("berlin", "VHS Berlin-Neukölln"): ["https://www.berlin.de/vhs-neukoelln/"],
    ("berlin", "Harri-Reinert"): ["https://www.berlin.de/vhs/volkshochschulen/spandau/"],
    ("berlin", "VHS Berlin Steglitz"): ["https://www.berlin.de/vhs/volkshochschulen/steglitz-zehlendorf/"],
    ("berlin", "VHS Berlin-Reinickendorf"): ["https://www.berlin.de/vhs/volkshochschulen/reinickendorf/"],
    ("berlin", "VHS Berlin-Marzahn"): ["https://www.berlin.de/vhs/volkshochschulen/marzahn-hellersdorf/"],
    ("berlin", "VHS Berlin Lichtenberg"): ["https://www.berlin.de/vhs/volkshochschulen/lichtenberg/"],
    ("berlin", "VHS Berlin Treptow"): ["https://www.berlin.de/vhs/volkshochschulen/treptow-koepenick/"],
    ("berlin", "VHS Berlin Friedrichshain"): ["https://www.berlin.de/vhs/volkshochschulen/friedrichshain-kreuzberg/"],
    ("berlin", "VHS Berlin-Pankow"): ["https://www.berlin.de/vhs/volkshochschulen/pankow/service/einbuergerungstest-vhs-pankow-1463977.php"],
    ("köln", "VHS der Stadt Köln"): ["https://www.koelner-vhs.de/deutsch-integration/einbuergerungstest"],
    ("münchen", "Münchner Volkshochschule"): ["https://www.mvhs.de/kurse/deutsch-integration/pruefungen-einbuergerung/einbuergerung-460-CAT-KAT7868"],
    ("ulm", "Ulmer Volkshochschule"): ["https://www.vh-ulm.de/vh-programm/kurs-finder?kfs_stichwort=&katzeitraumfilter=__reset__&katwotagefilter[]=__reset__&katkategorienfilter=2039"],
    ("wiesbaden", "VHS Wiesbaden"): ["https://www.vhs-wiesbaden.de/fachbereiche-und-projekte/deutsch/einbuergerungstest"],
    ("hannover", "BERGMANN"): ["https://www.bergmann-institut.org/einb%C3%BCrgerungstest"],
    ("erfurt", "Mitteldeutsches Institut"): ["https://mitteldeutsches-institut.de/einbuergerungstest-erfurt/"],
    ("chemnitz", "Mitteldeutsches Institut"): ["https://mitteldeutsches-institut.de/einbuergerungstest-chemnitz/"],
    ("leipzig", "VHS Stadt Leipzig"): ["https://www.vhs-leipzig.de/p/kurse/deutsch-integration/pruefungen/einbuergerungstest-495-C-G418881P"],
    ("hannover", "Verein für Integration"): ["https://www.sprachakademie.org/leben-in-deutschland/", "https://www.sprachakademie.org/dtz-telc-sprachpruefung/"],
}

MESI = {"januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6, "juli": 7, "august": 8,
        "september": 9, "oktober": 10, "november": 11, "dezember": 12, "jan": 1, "feb": 2, "mär": 3,
        "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9, "okt": 10, "nov": 11, "dez": 12}
RE_DATA = re.compile(
    r"(?<![\d.])(?P<g>\d{1,2})\.\s?(?P<m>\d{1,2})\.\s?(?P<a>20\d\d|\d\d)(?![\d])"
    r"|(?<!\d)(?P<g2>\d{1,2})\.\s*(?P<mt>" + "|".join(sorted(MESI, key=len, reverse=True)) + r")\.?\s+(?P<a2>20\d\d)",
    re.I)
RE_EBT = re.compile(r"einbürgerung|einbuergerung|leben in deutschland|\blid\b", re.I)
RE_DTZ = re.compile(r"\bdtz\b|test für zuwanderer|deutschtest für zuwanderer", re.I)
RE_TITOLO = re.compile(r"einbürgerung|leben in deutschland|\blid\b|\bdtz\b|zuwanderer|telc|goethe|testas|zertifikat|"
                       r"prüfung|pruefung|kurs|\b[abc][12]\b|modul", re.I)
RE_VICINO = re.compile(r"termin|prüfung|pruefung|\btest|wann", re.I)
RE_CORSO = re.compile(r"integrationskurs|alphabetisierung|umschulung|kursstart|starttermin|berufssprachkurs|"
                      r"vorbereitung|vorkurs|probetest|geschichte und politik|beratung|intensivkurs|kompakttraining|"
                      r"goethe|testas|zertifikat|telc deutsch b2|telc deutsch b1|\bb2\b|\bc1\b|\bc2\b|datum:", re.I)
RE_SCAD = re.compile(r"(anmeldeschluss|anmeldung bis|anmeldefrist|meldefrist|bis spätestens|rücktritt|abmeldung|bis)\W{0,4}$", re.I)
RE_APRE = re.compile(r"(anmeldung ab|anmeldung möglich ab|ab)\W{0,4}$", re.I)


def formato(url, testo_html):
    u = url.lower()
    if "-cat-kat" in u or re.search(r"-\d{3}-c-[a-z]?\d+", u):
        return "Kursportal VHS (itemKG/Kufer SQL)"
    if "/kategorie/" in u or "/kw/" in u or re.search(r"/kurs/[^/]+/[^/]+", u) or "kufer" in testo_html.lower()[:200000]:
        return "KuferWeb"
    if "berlitz" in u:
        return "Berlitz (elenco per città)"
    if "kurs-finder" in u or "vhs-hamburg.de" in u or "abendakademie" in u:
        return "altro catalogo corsi VHS"
    if "berlin.de" in u:
        return "portale berlin.de (testo libero)"
    return "pagina CMS con testo libero"


def decodifica(b):
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def testo(b):
    t = decodifica(b)
    titolo = re.search(r"(?is)<title[^>]*>(.*?)</title>", t)
    titolo = html.unescape(titolo.group(1)) if titolo else ""
    t = re.sub(r"(?is)<(script|style|noscript|nav|footer)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|td|th|h\d)>", " \n ", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return titolo, " ".join(t.split())


def estrai(url, titolo, t, solo_citta=None):
    """Restituisce le date d'esame future con tipo; solo_citta = taglia il testo al blocco di quella città (Berlitz)."""
    if solo_citta:
        i = t.find(solo_citta + " Prüfungstermine")
        if i < 0:
            return [], []
        j = t.find("Mehr erfahren", i)
        t = t[i: j if j > 0 else i + 600]
    intest = urllib.parse.unquote(url) + " " + titolo
    pagina_test = bool(RE_EBT.search(intest) or RE_DTZ.search(intest))
    pagina_tipo = "EBT" if RE_EBT.search(intest) else ("DTZ" if pagina_test else "")
    ms = list(RE_DATA.finditer(t))
    out, controlli = [], []
    for k, m in enumerate(ms):
        try:
            if m.group("g"):
                g, mese, a = int(m.group("g")), int(m.group("m")), int(m.group("a"))
            else:
                g, mese, a = int(m.group("g2")), MESI[m.group("mt").lower()], int(m.group("a2"))
            a = a + 2000 if a < 100 else a
            d = dt.date(a, mese, g)
        except (ValueError, KeyError):
            continue
        if not (OGGI < d <= FINE):
            continue
        # la "voce" della data: il testo dalla data precedente; se tra le due date non c'è un titolo
        # (solo orari, "ausgebucht", scadenze...) la data fa parte di un elenco e eredita l'intestazione
        # dell'elenco, cioè i 220 caratteri prima della prima data della fila
        prima_fine = ms[k - 1].end() if k else 0
        intervallo = t[prima_fine: m.start()]
        if k and len(intervallo) < 120 and not RE_TITOLO.search(intervallo):
            j = k - 1
            while j > 0 and (ms[j].start() - ms[j - 1].end()) < 120 and not RE_TITOLO.search(t[ms[j - 1].end(): ms[j].start()]):
                j -= 1
            voce = t[max(0, ms[j].start() - 220): ms[j].start()] + " … " + intervallo
        else:
            voce = intervallo[-220:] if k else t[max(0, m.start() - 220): m.start()]
        dopo = t[m.end(): m.end() + 60]
        # Euro-Schulen: la pagina della città contiene anche l'elenco nazionale; valgono solo le date "— <città>"
        if "euro-schulen.de/" in url:
            citta_url = url.split("euro-schulen.de/")[1].split("/")[0]
            m2 = re.match(r"\s*—\s*([^\s—]+)", dopo)
            norm = lambda x: x.lower().replace("ö", "oe").replace("ü", "ue").replace("ä", "ae")
            if not m2 or norm(m2.group(1)) != citta_url:
                continue
        # formato "data: titolo" (la data viene prima del nome dell'esame): conta il titolo dopo la data
        succ = ms[k + 1].start() if k + 1 < len(ms) else len(t)
        dopo_voce = re.sub(r"^[\s:–\-|,]*(?:(?:um\s)?\d{1,2}[:.]\d{2}(?:\s*(?:-|–)\s*\d{1,2}[:.]\d{2})?\s*(?:uhr)?[\s:,|–\-]*)?", "",
                           t[m.end(): min(succ, m.end() + 90)], flags=re.I)
        titolo_dopo = dopo_voce[:45] if RE_TITOLO.search(dopo_voce[:45]) and not re.match(r"(?i)\s*(\d|anmeld|bis|uhr)", dopo_voce) else ""
        if RE_SCAD.search(voce[-30:]):
            tipo_data = "scadenza iscrizione"
        elif RE_APRE.search(voce[-30:]):
            tipo_data = "apertura iscrizioni"
        else:
            tipo_data = "esame"
        if titolo_dopo:
            if RE_EBT.search(titolo_dopo):
                tipo = "EBT"
            elif RE_DTZ.search(titolo_dopo):
                tipo = "DTZ"
            else:
                continue  # dopo la data c'è il nome di un altro esame o corso
        elif RE_EBT.search(voce):
            tipo = "EBT"
        elif RE_DTZ.search(voce):
            tipo = "DTZ"
        elif pagina_test and RE_VICINO.search(voce):
            tipo = pagina_tipo
        else:
            continue
        # la voce più vicina parla di un corso o di un altro esame: non è una data del test
        ultimo = voce[-120:]
        if not titolo_dopo and RE_CORSO.search(ultimo) and not (RE_EBT.search(ultimo) or RE_DTZ.search(ultimo)):
            continue
        out.append({"data": d.isoformat(), "tipo": tipo, "tipo_data": tipo_data, "pagina": url})
        controlli.append({"data": d.isoformat(), "tipo": tipo, "tipo_data": tipo_data, "pagina": url,
                          "contesto": (voce[-160:] + " [[" + m.group(0) + "]] " + dopo)})
    return out, controlli


class Lettore:
    def __init__(self):
        self.s = requests.Session()
        self.robots = {}

    def ok(self, url, ua):
        p = urllib.parse.urlparse(url)
        h = p.scheme + "://" + p.netloc
        if h not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.s.get(h + "/robots.txt", headers={"User-Agent": ua}, timeout=15)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except Exception:
                rp.parse([])
            self.robots[h] = rp
        return self.robots[h].can_fetch(ua, url)

    def prendi(self, url):
        ua = UA_BERLINO if "berlin.de" in url else UA
        if not self.ok(url, ua):
            return None, "robots"
        time.sleep(3 if "berlin.de" in url else 0.8)
        try:
            r = self.s.get(url, headers={"User-Agent": ua, "Accept-Language": "de-DE,de;q=0.9"}, timeout=25)
        except Exception as e:
            return None, type(e).__name__
        if r.status_code != 200:
            return None, str(r.status_code)
        if "html" not in r.headers.get("content-type", ""):
            return None, "non HTML"
        return r.content, "200"


def pagine_trovate(i):
    """Pagine con date o parole chiave trovate dal crawler (due passate)."""
    urls = []
    for cartella in ("date", "date_passata1"):
        f = QUI / "grezzi" / cartella / f"{i:03d}.json"
        if not f.exists():
            continue
        r = json.loads(f.read_text())
        for p in r.get("pagine", []):
            if p.get("stato") == 200 and (p.get("n_date") or p.get("chiave")):
                if "berlin.de/vhs/volkshochschulen/pankow" in p["url"] and "pankow" not in r["url_partenza"]:
                    continue  # link comune del portale berlin.de, non è la pagina di questa VHS
                urls.append(p["url"])
    visti, out = set(), []
    for u in urls:
        k = u.split("?")[0].rstrip("/") if "kurs-finder" not in u else u
        if k not in visti:
            visti.add(k)
            out.append(u)
    # prima le pagine con parole del test nell'indirizzo
    out.sort(key=lambda u: 0 if re.search(r"einb|lid|leben|dtz|zuwander|pruef|prüf", u, re.I) else 1)
    return out[:8]


def main():
    tmp = pathlib.Path(sys.argv[1])
    sedi = json.loads((QUI / "grezzi" / "sedi_top20.json").read_text())
    lett = Lettore()
    cache = {}
    risultati, tutti_controlli = [], []
    for i, s in enumerate(sedi):
        pagine = []
        for (c, nome), us in PAGINE_A_MANO.items():
            if s["citta"] == c and s["nome"].startswith(nome):
                pagine += us
        if s["citta"] != "berlin":
            pagine += [u for u in pagine_trovate(i) if u not in pagine]
        date, formati, esiti = [], set(), []
        for u in pagine:
            if u not in cache:
                cache[u] = lett.prendi(u)
            corpo, stato = cache[u]
            esiti.append(stato)
            if corpo is None:
                continue
            titolo, t = testo(corpo)
            citta_berlitz = None
            if "berlitz" in u:
                citta_berlitz = {"köln": "Köln", "düsseldorf": "Düsseldorf", "hannover": "Hannover"}.get(s["citta"])
            d, ctrl = estrai(u, titolo, t, citta_berlitz)
            if d:
                formati.add(formato(u, decodifica(corpo)))
                date += d
                for x in ctrl:
                    x.update({"sede": s["nome"], "citta": s["citta"]})
                tutti_controlli += ctrl
        esami = sorted({(x["data"], x["tipo"]) for x in date if x["tipo_data"] == "esame"})
        risultati.append({
            "indice": i, "citta": s["citta"], "nome": s["nome"], "pagine_lette": len(pagine),
            "formati": sorted(formati),
            "date_esame_future": [{"data": a, "tipo": b} for a, b in esami],
            "date_iscrizione": sorted({x["data"] for x in date if x["tipo_data"] != "esame"}),
            "fonte": sorted({x["pagina"] for x in date}),
            "leggibile_ebt": any(t == "EBT" for _, t in esami),
            "leggibile_qualsiasi": bool(esami),
            "stati_http": esiti,
        })
        print(f"{i:03d} {s['citta']:<11} {s['nome'][:42]:<42} esami={len(esami):>2} "
              f"EBT={'sì' if any(t == 'EBT' for _, t in esami) else 'no'} {','.join(sorted(formati))}", flush=True)
    (QUI / "grezzi" / "estratte.json").write_text(json.dumps(risultati, ensure_ascii=False, indent=1))
    (tmp / "controlli.json").write_text(json.dumps(tutti_controlli, ensure_ascii=False, indent=1))
    n_ebt = sum(r["leggibile_ebt"] for r in risultati)
    n_any = sum(r["leggibile_qualsiasi"] for r in risultati)
    print(f"\nSEDI {len(risultati)} | con date future del Einbürgerungstest: {n_ebt} | con date future di EBT o DTZ: {n_any}")
    from collections import Counter
    c = Counter(f for r in risultati if r["leggibile_qualsiasi"] for f in r["formati"])
    print("formati:", c.most_common())


if __name__ == "__main__":
    main()
