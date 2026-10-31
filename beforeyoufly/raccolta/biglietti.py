"""Quando escono i biglietti delle grandi attrazioni (sezione "When do tickets go on sale?"): rilegge le fonti ufficiali.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/biglietti.py             rilegge le fonti, controlla le frasi citate, scrive dati/biglietti.json
    python3 -I beforeyoufly/raccolta/biglietti.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/biglietti/
    python3 -I beforeyoufly/raccolta/biglietti.py --domanda   rilegge anche l'autocompletamento di Google (dati/biglietti_domanda.json)
    python3 -I beforeyoufly/raccolta/biglietti.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 30/10/2026):
  - Solo le pagine ufficiali delle attrazioni (elenco in FONTI): museo, parco archeologico, fondazione, ente che le gestisce.
    Niente blog, guide, rivenditori di biglietti o venditori di visite guidate.
  - Le regole (giorno e ora di uscita dei biglietti, chiusure, giorni gratis) sono scritte a mano in dati/biglietti_manuali.json,
    ognuna legata alle frasi ufficiali che la dicono ("citazioni", parola per parola). Le date NON sono scritte a mano: le calcola
    genera.py dalla regola (prossimi 6 mesi) e verifica.py le ricalcola in modo indipendente.
  - Una regola diventa un calcolo solo se la frase ufficiale è chiara (giorno della settimana e ora, "first Sunday of the month",
    "last Sunday of the month" con le eccezioni scritte, date fisse). "Roughly two months", tabelle trimestrali senza il giorno o
    testi ufficiali in contrasto: solo la citazione, nessuna data calcolata.
  - La lettura vale solo con HTTP 200. Se una fonte non risponde 200 o se una citazione non c'è più nel testo normalizzato, lo script
    NON sovrascrive dati/biglietti.json ed esce con 1: si ricontrolla a mano.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte (dalla prima all'ultima frase citata). Se cambia, il cambio va
    in dati/biglietti_cambi.json: la pagina intorno alle citazioni è cambiata, rileggerla (può essere cambiata la regola).
  - Chiuse al server il 30/10/2026 (connessione interrotta o 403/000), quindi fuori dalla sezione: Colosseo e siti del Ministero
    della Cultura (colosseo.it, cultura.gov.it), Galleria Borghese, Acropoli e siti greci (odysseus.culture.gr, hhticket.gr), Prado,
    Torre Eiffel. tickets.museivaticani.va e tickets.alhambra-patronato.es non si leggono (certificato incompleto, controllo anti-robot):
    si linkano soltanto, perché le pagine ufficiali lette li indicano come unica biglietteria online.
  - Pagine grezze in raccolta/.cache/biglietti/ (escluse da git). Ricontrollo ogni mese (NOTE.md).
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "biglietti"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# id -> url, ente, titolo della pagina
FONTI = {
    "cen_info": {"url": "https://cenacolovinciano.org/en/info/", "ente": "Last Supper Museum (Museo del Cenacolo Vinciano)",
                 "titolo": "Cenacolo Vinciano: Info (tickets, hours)"},
    "vat_orari": {"url": "https://www.museivaticani.va/content/museivaticani-mobile/en/info/orari-musei-vaticani.html", "ente": "Vatican Museums",
                  "titolo": "Vatican Museums: Days & Hours of closure"},
    "vat_tariffe": {"url": "https://www.museivaticani.va/content/museivaticani-mobile/en/organizza-visita/tariffe-e-biglietti.html", "ente": "Vatican Museums",
                    "titolo": "Vatican Museums: Prices and Tickets"},
    "af_tickets": {"url": "https://www.annefrank.org/en/museum/tickets/", "ente": "Anne Frank House", "titolo": "Anne Frank House: Tickets"},
    "af_faq": {"url": "https://www.annefrank.org/en/museum/frequently-asked-questions/", "ente": "Anne Frank House",
               "titolo": "Anne Frank House: Frequently Asked Questions"},
    "pom_home": {"url": "https://pompeiisites.org/en/", "ente": "Archaeological Park of Pompeii", "titolo": "Pompeii Sites: official website"},
    "pom_orari": {"url": "https://pompeiisites.org/en/visiting-info/timetables-and-tickets/", "ente": "Archaeological Park of Pompeii",
                  "titolo": "Pompeii Sites: Timetables and tickets"},
    "alh_orari": {"url": "https://www.alhambra-patronato.es/en/visit/opening-hours-and-prices", "ente": "Patronato de la Alhambra y Generalife",
                  "titolo": "Alhambra: Opening hours and prices"},
    "alh_faq": {"url": "https://www.alhambra-patronato.es/en/visit/faq", "ente": "Patronato de la Alhambra y Generalife", "titolo": "Alhambra: Visit F.A.Q."},
    "alh_2018": {"url": "https://www.alhambra-patronato.es/en/notas-prensa/new-system-for-the-reservation-and-sale-of-tickets-to-the-alhambra",
                 "ente": "Patronato de la Alhambra y Generalife", "titolo": "Alhambra: New system for the reservation and sale of tickets (press release, 8 January 2018)"},
    "sf_faq": {"url": "https://sagradafamilia.org/en/faqs", "ente": "Basílica de la Sagrada Família", "titolo": "Sagrada Família: FAQs"},
    "sf_orari": {"url": "https://sagradafamilia.org/en/schedules-how-to-get", "ente": "Basílica de la Sagrada Família",
                 "titolo": "Sagrada Família: Opening hours and getting here"},
}

# Ricerche da rileggere con --domanda (autocompletamento, client=firefox, hl=en, gl=us e gl=uk): le FAQ si legano a queste
DOMANDA = [
    "when do last supper tickets go on sale", "last supper tickets", "last supper tickets release", "last supper milan tickets",
    "last supper free sunday", "is the last supper open on",
    "when do vatican tickets go on sale", "when do vatican museum tickets go on sale", "vatican museum free sunday",
    "is the vatican museum open on", "is the vatican open on", "vatican museums closed",
    "anne frank house tickets", "anne frank house tickets release", "when do anne frank house tickets go on sale",
    "anne frank house ticket release date", "is anne frank house open on",
    "when do pompeii tickets go on sale", "pompeii tickets", "pompeii free sunday", "is pompeii open on", "pompeii closed",
    "when do alhambra tickets go on sale", "alhambra tickets", "when are alhambra tickets released", "is the alhambra open on",
    "when do sagrada familia tickets go on sale", "sagrada familia tickets", "how far in advance sagrada familia tickets",
    "is sagrada familia open on",
]


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html,application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read()


def testo_fonte(raw):
    """Testo visibile normalizzato (come raccolta/gomme.py), senza trattini morbidi né spazi a larghezza zero."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", raw.decode("utf-8", "replace"))
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    for x in ("​", "⁣", "﻿", "\xad"):
        t = t.replace(x, "")
    t = re.sub(r"\s+", " ", t.replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def frasi_fonte(M, fid):
    return [c["x"] for a in M["attrazioni"] for c in a["citazioni"] if c["f"] == fid]


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return hashlib.sha256(testo[a:b].encode("utf-8")).hexdigest()[:16]


def file_cache(fid):
    return CACHE / f"{fid}.html"


def tutte_ricerche(D):
    return {s for g in D["ricerche"].values() for ss in g.values() for s in ss}


def domanda():
    out = {}
    for gl in ("us", "uk"):
        for q in DOMANDA:
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[2].decode("utf-8", "replace"))[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta
                print(f"  autocompletamento {gl} {q!r}: {e}")
                continue
            out.setdefault(gl, {})[q] = sugg
            time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=us e gl=uk) sull'uscita dei biglietti, le chiusure e i "
                    "giorni gratis delle attrazioni della sezione ticket-release-dates/. Ogni domanda delle FAQ è una di queste ricerche (campo 'query' "
                    "in biglietti_manuali.json). Riscritto da raccolta/biglietti.py --domanda.",
           "letto_il": date.today().isoformat(), "domande": DOMANDA, "ricerche": out}
    (DATI / "biglietti_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", sum(len(v) for g in out.values() for v in g.values()), "suggerimenti")


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "biglietti_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "biglietti_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "biglietti.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    usate = sorted({c["f"] for a in M["attrazioni"] for c in a["citazioni"]})
    problemi, letture, cambi = [], {}, []
    for fid in usate:
        F = FONTI.get(fid)
        if not F:
            problemi.append(f"fonte {fid} non in FONTI")
            continue
        f_cache = file_cache(fid)
        if da_cache:
            if not f_cache.exists():
                problemi.append(f"{fid}: nessuna copia in cache")
                continue
            P0 = prima["fonti"].get(fid) or {}
            raw, stato, finale = f_cache.read_bytes(), P0.get("http"), P0.get("url_finale")
        else:
            raw, errore = None, None
            for tentativo in range(4):
                try:
                    stato, finale, raw = leggi(F["url"])
                    break
                except Exception as e:
                    errore = e
                    time.sleep(5 + 10 * tentativo)
            if raw is None:
                problemi.append(f"{fid}: lettura fallita ({errore})")
                continue
            f_cache.write_bytes(raw)
        if stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
        t = testo_fonte(raw)
        frasi = frasi_fonte(M, fid)
        mancano = [x for x in frasi if x not in t]
        for x in mancano:
            problemi.append(f"{fid}: frase non trovata: {x[:90]!r}")
        imp = impronta_zona(t, frasi)
        P = prima["fonti"].get(fid) or {}
        letto = oggi if not da_cache else (P.get("letto_il") or oggi)
        cambiato = P.get("cambiato_il") if P.get("impronta") == imp and P.get("cambiato_il") else letto
        if P.get("impronta") and imp and P["impronta"] != imp:
            cambi.append({"data": oggi, "fonte": fid, "url": F["url"], "prima": P["impronta"], "dopo": imp})
            print(f"  CAMBIATA la zona citata di {fid}: rileggere la pagina (la regola può essere cambiata)")
        letture[fid] = {"url": F["url"], "pagina": F["url"], "url_finale": finale, "http": stato, "byte": len(raw), "ente": F["ente"],
                        "titolo": F["titolo"], "letto_il": letto, "cambiato_il": cambiato, "impronta": imp, "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {len(raw)} byte, {len(frasi)} frasi, {len(mancano)} mancanti, impronta {imp}")
    ricerche = tutte_ricerche(D)
    for a in M["attrazioni"]:
        ids = {c["id"] for c in a["citazioni"]}
        for q in a["faq"]:
            if q["query"] not in ricerche:
                problemi.append(f"{a['slug']}: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
            if any(i not in ids for i in q.get("cit", [])):
                problemi.append(f"{a['slug']}: FAQ «{q['q']}» con citazione sconosciuta")
        for r in a["uscite"] + ([a["gratis"]] if a.get("gratis") else []) + [a["chiusure"]]:
            if any(i not in ids for i in r.get("cit", [])):
                problemi.append(f"{a['slug']}: regola {r.get('id', r.get('tipo'))} con citazione sconosciuta")
    if problemi:
        print("NON SCRITTO dati/biglietti.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    doc = {"_nota": "Uscita dei biglietti, chiusure e giorni gratis delle grandi attrazioni: regole scritte a mano in dati/biglietti_manuali.json "
                    "(citazioni parola per parola), fonti rilette da raccolta/biglietti.py (HTTP, data di lettura, impronta della zona citata). "
                    "Le date le calcola genera.py dalle regole. Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "attrazioni": M["attrazioni"],
           "escluse": M["escluse"]}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "biglietti_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(M['attrazioni'])} attrazioni, {len(letture)} fonti" + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        f_cache = file_cache(fid)
        if not f_cache.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_cache.write_bytes(leggi(FONTI[fid]["url"])[2])
        print(testo_fonte(f_cache.read_bytes()))
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda()
        if "--solo-domanda" in sys.argv:
            sys.exit(0)
    main()
