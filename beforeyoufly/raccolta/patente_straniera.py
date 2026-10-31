"""Guidare in Canada, Australia e Nuova Zelanda con una patente straniera (sezione "foreign-licence-canada-australia-nz/").

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/patente_straniera.py             rilegge le fonti, controlla le frasi citate, scrive dati/patente_straniera.json
    python3 -I beforeyoufly/raccolta/patente_straniera.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/patente_straniera/
    python3 -I beforeyoufly/raccolta/patente_straniera.py --domanda   rilegge anche l'autocompletamento di Google (dati/patente_straniera_domanda.json)
    python3 -I beforeyoufly/raccolta/patente_straniera.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 31/10/2026):
  - Solo fonti ufficiali: ministeri, enti delle patenti delle province, degli stati e dei territori, NZ Transport Agency, siti
    ufficiali delle leggi (LegisQuébec). Niente scuole guida, broker, blog, compagnie di noleggio, traduttori.
  - I fatti sono scritti a mano in dati/patente_straniera_manuali.json: ogni frase mostrata sul sito tra virgolette è una citazione
    parola per parola ("citazioni"); le parole nostre (riassunti, risposta, FAQ) le controlla verifica.py (punto 23: nessun numero
    che non stia in una citazione).
  - La lettura vale solo con HTTP 200. Se una fonte non risponde 200 o se una citazione non c'è più nel testo normalizzato, lo script
    NON sovrascrive dati/patente_straniera.json ed esce con 1: si ricontrolla a mano.
  - Fonti NON lette ("bloccate"): le pagine ufficiali che dal server rispondono 403 o con una pagina di controllo anti-robot
    (Cloudflare, Incapsula, Radware). NON si aggirano (niente browser travestito, niente copie di terzi): lo script ritenta una volta
    con una richiesta normale e registra il codice e la data; la pagina del sito dice che la fonte non si è aperta e non scrive regole.
  - ICBC (British Columbia) carica l'elenco dei Paesi dentro i dati della pagina (Next.js, self.__next_f): al testo visibile si
    aggiungono le stringhe di quei dati, nell'ordine in cui arrivano (stesso contenuto della pagina, nessuna altra richiesta).
  - NZ Transport Agency: le pagine HTML rispondono con un controllo anti-robot; si legge il PDF ufficiale Factsheet 56 (pdftotext).
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte; se cambia, il cambio va in dati/patente_straniera_cambi.json.
  - Pagine grezze in raccolta/.cache/patente_straniera/ (escluse da git).
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "patente_straniera"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# id -> url, ente, titolo della pagina, tipo (html, next = html + dati Next.js, pdf)
FONTI = {
    # Canada
    "on_hb": {"url": "https://www.ontario.ca/document/official-mto-drivers-handbook/getting-your-drivers-licence",
              "ente": "Ontario Ministry of Transportation", "titolo": "Official MTO Driver's Handbook: Getting your driver's licence"},
    "on_x": {"url": "https://www.ontario.ca/page/exchange-out-province-drivers-licence",
             "ente": "Ontario Ministry of Transportation", "titolo": "Ontario.ca: Exchange an out-of-province driver's licence"},
    "bc_icbc": {"url": "https://icbc.com/driver-licensing/moving-bc/moving-from-another-country", "tipo": "next",
                "ente": "ICBC (Insurance Corporation of British Columbia)", "titolo": "ICBC: Moving from outside Canada"},
    "qc_csr": {"url": "https://www.legisquebec.gouv.qc.ca/en/document/cs/C-24.2",
               "ente": "Government of Québec (LegisQuébec)", "titolo": "LegisQuébec: Highway Safety Code (chapter C-24.2), sections 85 to 91"},
    "ab_x": {"url": "https://www.alberta.ca/exchange-non-alberta-licences",
             "ente": "Government of Alberta", "titolo": "Alberta.ca: Exchange a licence from outside Alberta"},
    "mb_new": {"url": "https://www.mpi.mb.ca/new-to-manitoba/",
               "ente": "Manitoba Public Insurance (MPI)", "titolo": "MPI: New to Manitoba"},
    "sk_prog": {"url": "https://sgi.sk.ca/handbook/-/knowledge_base/drivers/saskatchewan-driver-s-licence-program",
                "ente": "SGI (Saskatchewan Government Insurance)", "titolo": "Saskatchewan Driver's Handbook: Saskatchewan driver's licence program"},
    "sk_dl": {"url": "https://sgi.sk.ca/handbook/-/knowledge_base/drivers/driver-s-licence",
              "ente": "SGI (Saskatchewan Government Insurance)", "titolo": "Saskatchewan Driver's Handbook: Driver's licence"},
    "ns_x": {"url": "https://novascotia.ca/exchange-your-out-of-province-drivers-licence/",
             "ente": "Government of Nova Scotia", "titolo": "Novascotia.ca: Exchange Your Non-Nova Scotian Driver's Licence"},
    "ns_paal": {"url": "https://novascotia.ca/sns/paal/rmv/paal269.asp",
                "ente": "Government of Nova Scotia", "titolo": "Service Nova Scotia (Registry of Motor Vehicles): Driver's Licence"},
    "nb_new": {"url": "https://www.gnb.ca/en/topic/driving-transportation/driving-licensing/licences-new-residents.html",
               "ente": "Government of New Brunswick", "titolo": "GNB: Driver's licences for new residents"},
    "nl_app": {"url": "https://www.gov.nl.ca/motorregistration/new-residents-and-visitors/licence-application-process/",
               "ente": "Government of Newfoundland and Labrador (Motor Registration Division)", "titolo": "Motor Registration: Licence Application Process"},
    "nl_tr": {"url": "https://www.gov.nl.ca/motorregistration/new-residents-and-visitors/translation-of-foreign-driver-licences/",
              "ente": "Government of Newfoundland and Labrador (Motor Registration Division)", "titolo": "Motor Registration: Translation of Foreign Driver Licences"},
    "nt_fn": {"url": "https://www.idmv.inf.gov.nt.ca/Drivers/Drivers/Information-for-foreign-nationals",
              "ente": "Government of the Northwest Territories (Department of Infrastructure)", "titolo": "NWT Driver and Vehicle Services: Driver's Licence Information for Foreign Nationals"},
    # Australia
    "nsw_v": {"url": "https://www.nsw.gov.au/driving-boating-and-transport/driver-and-rider-licences/visiting-or-moving-to-nsw/visiting-from-overseas-or-interstate",
              "ente": "NSW Government", "titolo": "NSW Government: Driving with an overseas or interstate licence in NSW"},
    "nsw_m": {"url": "https://www.nsw.gov.au/driving-boating-and-transport/driver-and-rider-licences/visiting-or-moving-to-nsw/moving-your-overseas-licence",
              "ente": "NSW Government", "titolo": "NSW Government: Moving your overseas licence to NSW"},
    "nsw_x": {"url": "https://www.nsw.gov.au/driving-boating-and-transport/driver-and-rider-licences/visiting-or-moving-to-nsw/moving-your-overseas-licence/knowledge-and-driving-test-exemptions",
              "ente": "NSW Government", "titolo": "NSW Government: Knowledge and driving test exemptions"},
    "qld_v": {"url": "https://www.qld.gov.au/transport/licensing/driver-licensing/overseas/driving",
              "ente": "Queensland Government", "titolo": "Queensland Government: Driving in Queensland on an interstate or overseas licence"},
    "qld_t": {"url": "https://www.qld.gov.au/transport/licensing/driver-licensing/overseas/transfer",
              "ente": "Queensland Government", "titolo": "Queensland Government: Transferring to a Queensland licence"},
    "wa_v": {"url": "https://www.transport.wa.gov.au/licensing/visiting-from-overseas.asp",
             "ente": "Western Australia Department of Transport and Major Infrastructure", "titolo": "Transport WA: Visiting from overseas or interstate"},
    "wa_m": {"url": "https://www.transport.wa.gov.au/licensing/transferring-your-overseas-licence.asp",
             "ente": "Western Australia Department of Transport and Major Infrastructure", "titolo": "Transport WA: Moving from overseas"},
    # Nuova Zelanda
    "nz_56": {"url": "https://www.nzta.govt.nz/assets/resources/factsheets/56/docs/56-new-residents.pdf", "tipo": "pdf",
              "ente": "NZ Transport Agency Waka Kotahi", "titolo": "NZTA Factsheet 56: New residents and visitors – Driving in New Zealand (October 2026), PDF"},
}

# Pagine ufficiali che dal server NON si aprono (403 o pagina anti-robot): si ritenta con una richiesta normale e si registra l'esito.
BLOCCATE = {
    "qc_saaq": {"url": "https://saaq.gouv.qc.ca/en/drivers-licences/canadian-foreign-drivers-licence/non-resident-visitor-tourist-or-other-1", "ente": "SAAQ"},
    "pe": {"url": "https://www.princeedwardisland.ca/en/topic/driver-licensing", "ente": "Government of Prince Edward Island"},
    "yt": {"url": "https://yukon.ca/en/transfer-licence-registration", "ente": "Government of Yukon"},
    "nu": {"url": "https://www.gov.nu.ca/en/transportation/drivers-licence", "ente": "Government of Nunavut"},
    "vic": {"url": "https://www.vicroads.vic.gov.au/licences/convert-your-licence/driving-with-your-overseas-licence", "ente": "VicRoads"},
    "sa": {"url": "https://www.sa.gov.au/topics/driving-and-transport/licences/interstate-and-overseas/driving-with-an-overseas-licence", "ente": "SA.GOV.AU"},
    "tas": {"url": "https://www.transport.tas.gov.au/licensing/interstate_or_overseas_licences/driving_in_tasmania_on_an_interstate_or_overseas_licence",
            "ente": "Transport Tasmania"},
    "act": {"url": "https://www.accesscanberra.act.gov.au/driving-transport-and-parking/licences/drivers-with-licences-from-overseas", "ente": "Access Canberra"},
    "nt_au": {"url": "https://nt.gov.au/driving/licence/new-nt-residents-and-visitors/transfer-your-overseas-licence", "ente": "NT.GOV.AU"},
    "nz_web": {"url": "https://www.nzta.govt.nz/driver-licences/new-residents-and-visitors/driving-on-nz-roads/", "ente": "NZ Transport Agency Waka Kotahi"},
}
RX_ANTIROBOT = re.compile(r"Just a moment|_Incapsula_Resource|perfdrive\.com|Attention Required|cf-browser-verification", re.I)

# Ricerche da rileggere con --domanda (autocompletamento, client=firefox, hl=en, gl = us, uk, ca, au)
DOMANDA = ["can i drive in canada with", "can i drive in australia with", "can i drive in new zealand with", "driving in canada with",
           "driving in australia with", "driving in new zealand with", "how long can i drive in canada with", "how long can i drive in australia with",
           "how long can i drive in nz with", "how long can you drive in nz on", "can i drive in ontario with", "can i drive in bc with",
           "can i drive in quebec with", "can i drive in alberta with", "can i drive in nsw with", "can i drive in victoria with",
           "can i drive in queensland with", "can i drive in western australia with", "can i drive in tasmania with", "driving in ontario with",
           "driving in bc with", "driving in nsw with", "driving in queensland with", "international driving permit canada",
           "international driving permit australia", "foreign licence canada", "overseas licence australia", "overseas licence nz",
           "can i drive in nova scotia with", "can i drive in manitoba with", "can i drive in saskatchewan with", "can i drive in new brunswick with",
           "can i drive in newfoundland with", "can i drive in yukon with", "how long can you drive on an overseas licence in"]
GL = ("us", "uk", "ca", "au")


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html,application/pdf"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read()


def testo_html(html_):
    """Testo visibile normalizzato (come raccolta/gomme.py)."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    for x in ("​", "⁣", "﻿", "­"):
        t = t.replace(x, "")
    t = re.sub(r"\s+", " ", t.replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_next(html_):
    """Testo visibile + stringhe di testo dei dati Next.js (self.__next_f), nell'ordine in cui arrivano."""
    parti = [json.loads('"' + m + '"') for m in re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', html_)]
    stringhe = re.findall(r'\[false,"((?:[^"\\]|\\.)*)"\]', "".join(parti))
    extra = " ".join(json.loads('"' + s + '"') for s in stringhe)
    extra = re.sub(r"\s+", " ", extra.replace("\xa0", " "))
    return testo_html(html_) + " || " + re.sub(r" ([,.;:!?])", r"\1", extra).strip()


def testo_pdf(raw):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "f.pdf"
        f.write_bytes(raw)
        t = subprocess.run(["pdftotext", "-enc", "UTF-8", str(f), "-"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    t = re.sub(r"\s+", " ", t.replace("\f", " ").replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_fonte(raw, tipo="html"):
    if tipo == "pdf":
        return testo_pdf(raw)
    h = raw.decode("utf-8", "replace")
    return testo_next(h) if tipo == "next" else testo_html(h)


def frasi_fonte(M, fid):
    out = [c["x"] for p in M["giurisdizioni"] for c in p["citazioni"] if c["f"] == fid]
    for p in M["giurisdizioni"]:  # nomi dei Paesi degli elenchi di scambio: devono comparire nella fonte dell'elenco
        for e in p.get("scambio_elenchi", []):
            if e["f"] == fid:
                out += e["paesi_fonte"]
    return out


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return hashlib.sha256(testo[a:b].encode("utf-8")).hexdigest()[:16]


def file_cache(fid):
    return CACHE / f"{fid}.{'pdf' if FONTI[fid].get('tipo') == 'pdf' else 'html'}"


def tutte_ricerche(D):
    return {s for g in D["gl"].values() for ss in g.values() for s in ss}


def domanda():
    out = {}
    for gl in GL:
        for q in DOMANDA:
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[2].decode("utf-8", "replace"))[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta
                print(f"  autocompletamento {gl} {q!r}: {e}")
                continue
            out.setdefault(gl, {})[q] = sugg
            time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=us, uk, ca, au) su come guidare in Canada, Australia e "
                    "Nuova Zelanda con una patente straniera. Ogni domanda delle FAQ della sezione foreign-licence-canada-australia-nz/ è una di "
                    "queste ricerche (campo 'query' in patente_straniera_manuali.json). Riscritto da raccolta/patente_straniera.py --domanda.",
           "letto_il": date.today().isoformat(), "ricerche": DOMANDA, "gl": out}
    (DATI / "patente_straniera_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", len(tutte_ricerche(doc)), "suggerimenti diversi")


def prova_bloccate(da_cache, prima):
    """Una richiesta normale per ogni pagina bloccata: codice HTTP e se la risposta è una pagina anti-robot. Nessun aggiramento."""
    out = {}
    for bid, B in BLOCCATE.items():
        if da_cache:
            out[bid] = (prima.get("bloccate") or {}).get(bid) or {"url": B["url"], "ente": B["ente"], "http": None, "antirobot": None, "provato_il": None}
            continue
        try:
            stato, finale, raw = leggi(B["url"])
        except urllib.error.HTTPError as e:
            stato, finale, raw = e.code, B["url"], e.read() or b""
        except Exception as e:
            stato, finale, raw = 0, B["url"], str(e).encode()
        anti = bool(RX_ANTIROBOT.search(raw[:20000].decode("utf-8", "replace"))) or "perfdrive" in (finale or "")
        out[bid] = {"url": B["url"], "ente": B["ente"], "http": stato, "antirobot": anti, "provato_il": date.today().isoformat()}
        print(f"  bloccata {bid}: HTTP {stato}{', pagina anti-robot' if anti else ''}")
        time.sleep(0.5)
    return out


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "patente_straniera_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "patente_straniera_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "patente_straniera.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    usate = sorted({c["f"] for p in M["giurisdizioni"] for c in p["citazioni"]})
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
                except urllib.error.HTTPError as e:
                    errore = e  # 403/anti-bot o altro rifiuto del server: non si riprova (regola: non aggirare i blocchi)
                    break
                except Exception as e:
                    errore = e  # solo errori di rete/timeout: si riprova
                    time.sleep(5 + 10 * tentativo)
            if raw is None:
                problemi.append(f"{fid}: lettura fallita ({errore})")
                continue
            f_cache.write_bytes(raw)
        if stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
        t = testo_fonte(raw, F.get("tipo", "html"))
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
            print(f"  CAMBIATA la zona citata di {fid}: rileggere la pagina")
        letture[fid] = {"url": F["url"], "url_finale": finale, "http": stato, "byte": len(raw), "ente": F["ente"], "titolo": F["titolo"],
                        "tipo": F.get("tipo", "html"), "letto_il": letto, "cambiato_il": cambiato, "impronta": imp, "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {len(raw)} byte, {len(frasi)} frasi, {len(mancano)} mancanti, impronta {imp}")
    ricerche = tutte_ricerche(D)
    for p in M["giurisdizioni"]:
        for q in p.get("faq", []):
            if q["query"] not in ricerche:
                problemi.append(f"{p['id']}: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
    for q in M.get("faq_indice", []):
        if q["query"] not in ricerche:
            problemi.append(f"indice: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
    if problemi:
        print("NON SCRITTO dati/patente_straniera.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    bloccate = prova_bloccate(da_cache, prima)
    doc = {"_nota": "Guidare in Canada, Australia e Nuova Zelanda con una patente straniera: fatti scritti a mano in "
                    "dati/patente_straniera_manuali.json (citazioni parola per parola), fonti rilette da raccolta/patente_straniera.py (HTTP, data "
                    "di lettura, impronta della zona citata); 'bloccate' = pagine ufficiali che dal server non si aprono (non aggirate). "
                    "Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "bloccate": bloccate,
           "giurisdizioni": M["giurisdizioni"], "faq_indice": M.get("faq_indice", [])}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "patente_straniera_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(M['giurisdizioni'])} giurisdizioni, {len(letture)} fonti lette, "
          f"{len(bloccate)} pagine bloccate" + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        F = FONTI[fid]
        f_cache = file_cache(fid)
        if not f_cache.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_cache.write_bytes(leggi(F["url"])[2])
        print(testo_fonte(f_cache.read_bytes(), F.get("tipo", "html")))
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda()
        if "--solo-domanda" in sys.argv:
            sys.exit(0)
    main()
