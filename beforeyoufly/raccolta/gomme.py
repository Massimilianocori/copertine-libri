"""Gomme invernali e catene con l'auto a noleggio (sezione "Winter tyres and snow chains with a rental car"): rilegge le fonti ufficiali.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/gomme.py             rilegge le fonti, controlla le frasi citate, scrive dati/gomme.json
    python3 -I beforeyoufly/raccolta/gomme.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/gomme/
    python3 -I beforeyoufly/raccolta/gomme.py --domanda   rilegge anche l'autocompletamento di Google (dati/gomme_domanda.json)
    python3 -I beforeyoufly/raccolta/gomme.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 30/10/2026):
  - Solo fonti ufficiali: ministeri, polizia, agenzie pubbliche per la sicurezza stradale, portali del governo, Gazzette/leggi (elenco in FONTI).
    Niente club automobilistici, niente produttori di pneumatici, niente siti di noleggiatori.
  - I fatti sono scritti a mano in dati/gomme_manuali.json: ogni frase mostrata sul sito tra virgolette è una citazione parola per parola
    ("citazioni"); le parole nostre (risposta, periodo, catene, FAQ) le controlla verifica.py (punto 21: nessun numero che non stia in una citazione).
  - La lettura vale solo con HTTP 200. Se una fonte non risponde 200 o se una citazione non c'è più nel testo normalizzato, lo script NON
    sovrascrive dati/gomme.json ed esce con 1: si ricontrolla a mano.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte (dalla prima all'ultima frase citata). Se cambia, il cambio va in
    dati/gomme_cambi.json: la pagina intorno alle citazioni è cambiata, rileggerla.
  - PDF (direttiva del Ministero delle infrastrutture e dei trasporti): testo estratto con pdftotext (poppler-utils), spazi unificati.
  - www.mit.gov.it manda solo il proprio certificato, senza il certificato intermedio (i browser lo scaricano da soli): si aggiunge
    alla verifica TLS il certificato intermedio pubblico "Sectigo Public Server Authentication CA DV R36" (preso dall'elenco ufficiale
    CCADB di Mozilla, file certificati/sectigo_dv_r36.pem). La verifica del certificato resta attiva.
  - Pagine grezze in raccolta/.cache/gomme/ (escluse da git). Ricontrollo completo ogni ottobre, prima della stagione.
"""
import hashlib
import json
import re
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "gomme"
CERT_MIT = Path(__file__).resolve().parent / "certificati" / "sectigo_dv_r36.pem"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# id -> url, ente, titolo della pagina, lingua, tipo (html o pdf), cert (certificato intermedio da aggiungere)
FONTI = {
    "it_mit": {"url": "https://www.mit.gov.it/nfsmitgov/files/media/normativa/2017-09/direttiva_ministeriale_prototocollo_1580_del_16-01-2013.pdf",
               "ente": "Italian Ministry of Infrastructure and Transport", "titolo": "MIT: Direttiva sulla circolazione stradale in periodo invernale (prot. 1580, 16 January 2013), PDF",
               "lingua": "it", "tipo": "pdf", "cert": True},
    "it_polizia": {"url": "https://www.poliziadistato.it/articolo/dal-15-novembre-scatta-l-obbligo-degli-pneumatici-invernali",
                   "ente": "Polizia di Stato (Italian State Police)", "titolo": "Polizia di Stato: Dal 15 novembre scatta l'obbligo degli pneumatici invernali", "lingua": "it"},
    "at_bmimi": {"url": "https://www.bmimi.gv.at/en/topics/transport/roads/safety/tyres.html",
                 "ente": "Austrian Federal Ministry for Innovation, Mobility and Infrastructure", "titolo": "BMIMI: Winter tyres and snow chains"},
    "de_bmv": {"url": "https://www.bmv.de/SharedDocs/DE/Artikel/StV/Strassenverkehr/winterreifen.html",
               "ente": "German Federal Ministry of Transport", "titolo": "BMV: Winterreifenpflicht", "lingua": "de"},
    "de_stvo3": {"url": "https://www.gesetze-im-internet.de/stvo_2013/__3.html",
                 "ente": "German Federal Ministry of Justice (Gesetze im Internet)", "titolo": "Straßenverkehrs-Ordnung (StVO), § 3", "lingua": "de"},
    "de_stvo": {"url": "https://www.gesetze-im-internet.de/stvo_2013/__2.html",
                "ente": "German Federal Ministry of Justice (Gesetze im Internet)", "titolo": "Straßenverkehrs-Ordnung (StVO), § 2", "lingua": "de"},
    "fr_sp": {"url": "https://www.service-public.gouv.fr/particuliers/actualites/A14389",
              "ente": "Service-Public.fr (French government)", "titolo": "Service-Public.fr: Pneus hiver, chaînes : quelles sont vos obligations jusqu'au 31 mars 2027 ?", "lingua": "fr"},
    "ch_chch": {"url": "https://www.ch.ch/en/travel-and-emigrate/holidays-in-switzerland/how-to-behave-in-road-traffic/winter-tyres/",
                "ente": "ch.ch (Swiss Confederation, cantons and communes)", "titolo": "ch.ch: Are winter tyres compulsory?"},
    "si_avp": {"url": "https://portalspv.avp-rs.si/novica?post=Spet+je+cas+za+zimsko+%27obutev%27",
               "ente": "Slovenian Traffic Safety Agency (AVP)", "titolo": "AVP: Spet je čas za zimsko 'obutev'", "lingua": "sl"},
    "si_sto": {"url": "https://www.slovenia.info/en/plan-your-trip/getting-to-and-around-slovenia/to-slovenia-by-car",
               "ente": "Slovenian Tourist Board", "titolo": "Slovenia.info: Driving to and around Slovenia"},
    "hr_policija": {"url": "https://zagrebacka-policija.gov.hr/vijesti/koristenje-zimske-opreme-na-vozilima-obvezno-od-15-studenoga-2024-do-15-travnja-2025-godine/99415",
                    "ente": "Croatian Police (Zagreb Police Administration)", "titolo": "Zagreb Police: Korištenje zimske opreme na vozilima obvezno od 15. studenoga", "lingua": "hr"},
    "cz_md": {"url": "https://md.gov.cz/Media/Media-a-tiskove-zpravy/Ridicum-zacala-povinnost-prezout-na-zimni-pneumati",
              "ente": "Czech Ministry of Transport", "titolo": "Ministerstvo dopravy: Řidičům začala povinnost přezout na zimní pneumatiky", "lingua": "cs"},
    "sk_portal": {"url": "https://www.slovensko.sk/sk/zivotne-situacie/zivotna-situacia/_pravidla-cestnej-premavky/",
                  "ente": "Slovensko.sk (Slovak government portal)", "titolo": "Slovensko.sk: Pravidlá cestnej premávky", "lingua": "sk"},
    "no_vv": {"url": "https://www.vegvesen.no/en/vehicles/own-and-maintain/tyre-requirements/",
              "ente": "Norwegian Public Roads Administration (Statens vegvesen)", "titolo": "Statens vegvesen: Tyre requirements"},
    "se_ts": {"url": "https://www.transportstyrelsen.se/en/road/vehicles/winter-tyres/",
              "ente": "Swedish Transport Agency (Transportstyrelsen)", "titolo": "Transportstyrelsen: Winter tyres"},
    "fi_traficom": {"url": "https://traficom.fi/en/news/remember-check-condition-and-symbols-winter-tyres-non-studded-winter-tyres-must-have-three-peak-mountain-snowflake-symbol",
                    "ente": "Finnish Transport and Communications Agency (Traficom)", "titolo": "Traficom: Remember to check the condition and symbols of winter tyres"},
    "es_dgt": {"url": "https://www.dgt.es/comunicacion/notas-de-prensa/nevadas-imprescindible-consultar-el-estado-de-las-carreteras-y-llevar-cadenas-o-neumaticos-de-invierno/",
               "ente": "Spanish Directorate-General for Traffic (DGT)", "titolo": "DGT: Nevadas: imprescindible consultar el estado de las carreteras y llevar cadenas o neumáticos de invierno",
               "lingua": "es"},
    "ad_govern": {"url": "https://www.govern.ad/ca/tematiques/comerc-i-consum/consum/consells-de-consum/informacio-pneumatics",
                  "ente": "Government of Andorra", "titolo": "Govern d'Andorra: Informació sobre els pneumàtics", "lingua": "ca"},
    "ad_mobilitat": {"url": "https://www.mobilitat.ad/colors-neu", "ente": "Andorra Department of Mobility", "titolo": "Departament de Mobilitat: Colors de la Neu", "lingua": "ca"},
}

# Ricerche da rileggere con --domanda (autocompletamento, client=firefox, hl=en, gl=uk e gl=us)
DOMANDA_PAESI = {"IT": "italy", "AT": "austria", "DE": "germany", "FR": "france", "CH": "switzerland", "SI": "slovenia", "HR": "croatia",
                 "CZ": "czech republic", "SK": "slovakia", "NO": "norway", "SE": "sweden", "FI": "finland", "ES": "spain", "AD": "andorra"}
DOMANDA_MODELLI = ["winter tyres {p}", "winter tires {p}", "snow chains {p}", "snow chains rental car {p}", "are winter tyres mandatory in {p}",
                   "are winter tires mandatory in {p}", "do you need snow chains in {p}"]
DOMANDA_EXTRA = ["winter tyres ", "winter tires ", "winter tyres rental car", "winter tires rental car", "snow chains rental car", "snow chains hire car"]
# Una pagina Paese esiste solo se almeno MIN_RICERCHE ricerche vere (suggerimenti diversi) nominano il Paese e le gomme invernali o le catene
MIN_RICERCHE = 5
NOMI_RICERCA = {"IT": "italy|italia", "AT": "austria", "DE": "germany", "FR": "france", "CH": "switzerland|swiss", "SI": "slovenia", "HR": "croatia",
                "CZ": "czech", "SK": "slovakia", "NO": "norway", "SE": "sweden", "FI": "finland", "ES": "spain", "AD": "andorra"}
TEMA_RICERCA = re.compile(r"winter (?:tyre|tire)|snow ?chain|snow socks|tyre chains|tire chains", re.I)


def contesto_tls(F):
    ctx = ssl.create_default_context()
    if F.get("cert"):
        ctx.load_verify_locations(cafile=str(CERT_MIT))  # aggiunge il certificato intermedio; la verifica resta attiva
    return ctx


def leggi(url, F=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html,application/pdf,application/json"})
    with urllib.request.urlopen(req, timeout=60, context=contesto_tls(F or {})) as r:
        return r.status, r.geturl(), r.read()


def testo_html(html_):
    """Testo visibile normalizzato (come raccolta/pedaggi.py), senza trattini morbidi."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    for x in ("​", "⁣", "﻿", "­"):
        t = t.replace(x, "")
    t = re.sub(r"\s+", " ", t.replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_pdf(raw):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "f.pdf"
        f.write_bytes(raw)
        t = subprocess.run(["pdftotext", "-enc", "UTF-8", str(f), "-"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    t = re.sub(r"\s+", " ", t.replace("\f", " ").replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_fonte(raw, tipo="html"):
    """raw: bytes della pagina salvata."""
    if tipo == "pdf":
        return testo_pdf(raw)
    return testo_html(raw.decode("utf-8", "replace"))


def frasi_fonte(M, fid):
    return [c["x"] for p in M["paesi"] for c in p["citazioni"] if c["f"] == fid]


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return hashlib.sha256(testo[a:b].encode("utf-8")).hexdigest()[:16]


def file_cache(fid):
    return CACHE / f"{fid}.{'pdf' if FONTI[fid].get('tipo') == 'pdf' else 'html'}"


def ricerche_paese(D, c):
    """Ricerche vere (suggerimenti) che nominano il Paese e le gomme invernali o le catene."""
    nome = re.compile(r"\b(?:" + NOMI_RICERCA[c] + r")", re.I)
    tutte = {s for g in D["paesi"].values() for qq in g.values() for ss in qq.values() for s in ss}
    return sorted(s for s in tutte if nome.search(s) and TEMA_RICERCA.search(s))


def domanda():
    out = {}
    for gl in ("uk", "us"):
        query = [(c, m.format(p=p)) for c, p in DOMANDA_PAESI.items() for m in DOMANDA_MODELLI] + [("_extra", q) for q in DOMANDA_EXTRA]
        for c, q in query:
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[2].decode("utf-8", "replace"))[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta
                print(f"  autocompletamento {gl} {q!r}: {e}")
                continue
            out.setdefault(c, {}).setdefault(gl, {})[q] = sugg
            time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=uk e gl=us) su gomme invernali e catene, anche con l'auto a "
                    "noleggio. Una pagina Paese della sezione winter-tyres-rental-car/ esiste solo se almeno un suggerimento nomina il Paese e le gomme "
                    "invernali o le catene in almeno 5 suggerimenti diversi (raccolta/gomme.py, ricerche_paese, MIN_RICERCHE); ogni domanda delle FAQ è una di queste ricerche (campo 'query' in "
                    "gomme_manuali.json). Riscritto da raccolta/gomme.py --domanda.",
           "letto_il": date.today().isoformat(), "modelli": DOMANDA_MODELLI, "extra": DOMANDA_EXTRA, "paesi": out}
    (DATI / "gomme_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", {c: len(ricerche_paese(doc, c)) for c in DOMANDA_PAESI})


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "gomme_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "gomme_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "gomme.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    usate = sorted({c["f"] for p in M["paesi"] for c in p["citazioni"]})
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
            raw = None
            for tentativo in range(4):
                try:
                    stato, finale, raw = leggi(F["url"], F)
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
        letture[fid] = {"url": F["url"], "pagina": F["url"], "url_finale": finale, "http": stato, "byte": len(raw), "ente": F["ente"],
                        "titolo": F["titolo"], "lingua": F.get("lingua", "en"), "tipo": F.get("tipo", "html"), "letto_il": letto,
                        "cambiato_il": cambiato, "impronta": imp, "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {len(raw)} byte, {len(frasi)} frasi, {len(mancano)} mancanti, impronta {imp}")
    for p in M["paesi"]:
        for q in p["faq"]:
            if q["query"] not in {s for g in D["paesi"].values() for qq in g.values() for ss in qq.values() for s in ss}:
                problemi.append(f"{p['iso2']}: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
    if problemi:
        print("NON SCRITTO dati/gomme.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    pagine = sorted(p["iso2"] for p in M["paesi"] if len(ricerche_paese(D, p["iso2"])) >= MIN_RICERCHE)
    doc = {"_nota": "Gomme invernali e catene con l'auto a noleggio: fatti scritti a mano in dati/gomme_manuali.json (citazioni parola per parola), "
                    "fonti rilette da raccolta/gomme.py (HTTP, data di lettura, impronta della zona citata). 'pagine' = Paesi con una pagina propria "
                    "(ricerche vere in dati/gomme_domanda.json). Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "pagine": pagine, "paesi": M["paesi"]}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "gomme_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(M['paesi'])} Paesi ({len(pagine)} con pagina), {len(letture)} fonti"
          + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        F = FONTI[fid]
        f_cache = file_cache(fid)
        if not f_cache.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_cache.write_bytes(leggi(F["url"], F)[2])
        print(testo_fonte(f_cache.read_bytes(), F.get("tipo", "html")))
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda()
        if "--solo-domanda" in sys.argv:
            sys.exit(0)
    main()
