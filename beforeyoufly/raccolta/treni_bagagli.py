"""Bagagli sui treni per compagnia (sezione "train-luggage-rules/") e orari di arrivo in stazione di Eurostar con l'EES
(pagina "eurostar-check-in-times/").

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/treni_bagagli.py             rilegge le fonti, controlla le frasi citate, scrive dati/treni_bagagli.json
    python3 -I beforeyoufly/raccolta/treni_bagagli.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/treni_bagagli/
    python3 -I beforeyoufly/raccolta/treni_bagagli.py --domanda   rilegge anche l'autocompletamento di Google (dati/treni_bagagli_domanda.json)
    python3 -I beforeyoufly/raccolta/treni_bagagli.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Perché un file nuovo e non raccolta/bagagli.py: quello rilegge con il browser le pagine del bagaglio a mano delle compagnie AEREE
(dati/bagagli.json, formato diverso); qui le pagine delle compagnie ferroviarie si leggono con una richiesta normale, come
raccolta/trasporti.py, con lo stesso testo normalizzato.

Regole (decise il 31/10/2026):
  - Solo fonti ufficiali: le pagine della compagnia ferroviaria (o il sito di vendita della stessa compagnia, come SNCF Connect per
    TGV INOUI). Niente blog, guide, forum, rivenditori di biglietti, siti di confronto, servizi di deposito bagagli.
  - I fatti sono scritti a mano in dati/treni_bagagli_manuali.json: ogni frase mostrata sul sito tra virgolette è una citazione parola per
    parola; i riassunti nostri (numero, misure, peso, supplementi, risposta, FAQ, traduzioni) li controlla verifica.py (punto 25: nessun
    numero che non stia in una citazione della stessa compagnia).
  - Una compagnia ha una pagina solo se la sua pagina ufficiale attuale si apre (HTTP 200) e dice quanti bagagli o quanto grandi.
    Le altre restano nell'indice come "Not read" con il motivo, senza dati.
  - Orari Eurostar: ogni riga della tabella per stazione (minuti di arrivo consigliati e chiusura dei cancelli) è controllata contro il
    testo della tabella ufficiale ricomposto parola per parola (funzione riga_stazione, la usa anche verifica.py).
  - La lettura vale solo con HTTP 200. NESSUN nuovo tentativo su HTTPError (403, 404, 5xx...) né su pagine anti-robot o captcha: non si
    aggirano i blocchi; si riprova solo per errori di rete o di tempo (connessione chiusa, timeout), al massimo 3 volte. Se una fonte non
    risponde 200 o una citazione non c'è più, lo script NON sovrascrive dati/treni_bagagli.json ed esce con 1: si ricontrolla a mano.
  - Compagnie non lette: UNA richiesta normale alla pagina ufficiale provata; si registrano codice, pagina anti-robot sì/no e data.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte; se cambia, il cambio va in dati/treni_bagagli_cambi.json.
  - Pagine grezze in raccolta/.cache/treni_bagagli/ (escluse da git).
  - Ripetibilità (revisione del 31/10/2026): servono solo questo file e dati/treni_bagagli_manuali.json (+ _domanda.json). La prima stesura
    di _manuali.json era uscita da uno script di partenza fuori dal repository: non serve più, _manuali.json si corregge a mano e i controlli
    che faceva quello script (citazioni nel testo, id unici, FAQ con id esistenti) sono qui (controlla_struttura e il ciclo sulle fonti).
    Da un clone pulito senza cache: lanciare senza --cache (rilegge le fonti in rete); --cache funziona solo dopo una lettura in rete.
  - Ricontrollo: ogni 3 mesi, e prima di dicembre e di giugno (orari invernali/estivi delle compagnie).
"""
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "treni_bagagli"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# id -> url, ente, titolo della pagina, lingua delle citazioni
FONTI = {
    "es_lug": {"url": "https://www.eurostar.com/uk-en/travel-info/travel-planning/luggage", "ente": "Eurostar",
               "titolo": "Eurostar luggage allowance: size, weight and baggage rules", "lingua": "en"},
    "es_help": {"url": "https://help.eurostar.com/faq/us-en/question/How-much-luggage-can-I-take", "ente": "Eurostar",
                "titolo": "Eurostar Help Centre: What luggage can I take onboard?", "lingua": "en"},
    "es_checkin": {"url": "https://www.eurostar.com/uk-en/travel-info/your-trip/check-in", "ente": "Eurostar",
                   "titolo": "Eurostar: When to arrive at the station", "lingua": "en"},
    "es_ees": {"url": "https://help.eurostar.com/faq/us-en/question/What-s-the-EU-s-Entry-Exit-System-EES", "ente": "Eurostar",
               "titolo": "Eurostar Help Centre: What's the EU's Entry/Exit System (EES)?", "lingua": "en"},
    "es_stp": {"url": "https://www.eurostar.com/uk-en/travel-info/your-trip/stations/london-st-pancras-international", "ente": "Eurostar",
               "titolo": "Eurostar: London St Pancras train station guide", "lingua": "en"},
    "sncf": {"url": "https://www.sncf-connect.com/en-en/help/transport-luggage", "ente": "SNCF Connect (SNCF)",
             "titolo": "SNCF Connect: What are the terms and conditions for carrying my luggage?", "lingua": "en"},
    "ouigo_fr": {"url": "https://www.ouigo.com/fr-en/packs-et-options/bagages", "ente": "OUIGO (SNCF Voyageurs)",
                 "titolo": "OUIGO luggage: dimensions, prices and options", "lingua": "en"},
    "ouigo_es": {"url": "https://www.ouigo.com/es/nuestro-producto", "ente": "OUIGO España",
                 "titolo": "OUIGO España: Viajar en tren barato por España", "lingua": "es"},
    "renfe": {"url": "https://www.renfe.com/es/en/travel/informacion-util/luggage/politica-de-equipajes", "ente": "Renfe",
              "titolo": "Renfe: Carrying luggage on the train", "lingua": "en"},
    "renfe_esp": {"url": "https://www.renfe.com/es/en/travel/informacion-util/luggage/equipajes-especiales", "ente": "Renfe",
                  "titolo": "Renfe: Bring your special luggage on the train", "lingua": "en"},
    "avlo": {"url": "https://www.renfe.com/es/en/travel/prepare-your-trip/quiero-avlo/tarifas-y-servicios", "ente": "Renfe",
             "titolo": "Renfe: Avlo fares and services", "lingua": "en"},
    "tit_faq": {"url": "https://www.trenitalia.com/en/information/faqs-section.html", "ente": "Trenitalia", "titolo": "Trenitalia: FAQs",
                "lingua": "en"},
    "italo": {"url": "https://www.italotreno.com/en/the-train/luggage", "ente": "Italo (Italo – Nuovo Trasporto Viaggiatori)",
              "titolo": "Italo's Luggage Policy", "lingua": "en"},
    "db": {"url": "https://int.bahn.de/en/trains/luggage", "ente": "Deutsche Bahn", "titolo": "Deutsche Bahn: Luggage on the train", "lingua": "en"},
    "oebb": {"url": "https://www.oebb.at/static/tarife/en/guide_for_travelling_with_oebb_in_austria/index.html", "ente": "ÖBB (Austrian Federal Railways)",
             "titolo": "ÖBB Fare Rules: Guide for travelling with ÖBB in Austria (valid from 15.10.2026)", "lingua": "en"},
    "nightjet": {"url": "https://www.nightjet.com/en/buchung/faq/service-und-austattung", "ente": "ÖBB Nightjet",
                 "titolo": "Nightjet: FAQs – Service and amenities", "lingua": "en"},
    "nsi": {"url": "https://www.nsinternational.com/en/travel-information/before-you-go/luggage", "ente": "NS International",
            "titolo": "NS International: Luggage on the train", "lingua": "en"},
    "lyria": {"url": "https://www.tgv-lyria.com/fr/en/train-travel/onboard-services/luggage-bicycles", "ente": "TGV Lyria",
              "titolo": "TGV Lyria: Luggage and bicycle transport on board", "lingua": "en"},
    "lumo": {"url": "https://www.lumo.co.uk/plan-your-journey/onboard-luggage-policy", "ente": "Lumo", "titolo": "Lumo: Onboard luggage policy",
             "lingua": "en"},
    "avanti": {"url": "https://www.avantiwestcoast.co.uk/onboard/luggage", "ente": "Avanti West Coast", "titolo": "Avanti West Coast: Luggage",
               "lingua": "en"},
}
RX_ANTIROBOT = re.compile(r"Just a moment|_Incapsula_Resource|perfdrive\.com|Radware|Attention Required|cf-browser-verification|captcha|"
                          r"Please enable JS and disable any ad blocker|Access to this page has been denied", re.I)

# Ricerche dell'autocompletamento: nome della compagnia come lo scrive la gente
NOMI_DOMANDA = ["eurostar", "sncf", "tgv", "tgv inoui", "ouigo", "ouigo spain", "iryo", "renfe", "ave", "avlo", "trenitalia", "frecciarossa",
                "italo", "db", "deutsche bahn", "ice train", "obb", "nightjet", "railjet", "sbb", "ns international", "eurocity direct",
                "trenitalia france", "tgv lyria", "lyria", "lumo", "lner", "avanti west coast", "avanti"]
MODELLI_DOMANDA = ["{c} luggage", "{c} luggage allowance", "{c} luggage size", "{c} luggage rules"]
EXTRA_DOMANDA = ["luggage on trains", "luggage allowance on trains", "luggage allowance on trains in", "train luggage europe",
                 "luggage on european trains", "eurostar check in", "eurostar check in time", "eurostar check in time st pancras",
                 "eurostar ees", "eurostar arrival time", "how early to arrive for eurostar", "eurostar gate closing time"]
GL = ("us", "uk")


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        return r.status, r.geturl(), (gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def testo_html(html_):
    """Testo visibile normalizzato (stesso metodo di raccolta/trasporti.py)."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    for x in ("​", "⁣", "﻿", "­"):
        t = t.replace(x, "")
    t = re.sub(r"\s+", " ", t.replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_fonte(raw):
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return testo_html(raw.decode("utf-8", "replace"))


def citazioni_tutte(M):
    """Tutte le citazioni dei dati: compagnie e pagina Eurostar."""
    out = [c for p in M["compagnie"] for c in p.get("citazioni", [])]
    return out + list(M.get("eurostar", {}).get("citazioni", []))


def riga_stazione(s):
    """Testo della riga della tabella ufficiale Eurostar per una stazione, come risulta dal testo normalizzato della pagina."""
    a, c = s["arrivo"], s["chiusura"]
    chiude = "does the gate close" if s["chiusura_tipo"] == "gate" else "do ticket checks close"
    return (f"{s['nome']} Eurostar Standard & Eurostar Plus Eurostar Premier Accessible travel How long before departure should I arrive? (mins) "
            f"{a['standard']} {a['premier']} {a['accessibile']} How long before departure {chiude}? (mins) {c['standard']} {c['premier']} {c['accessibile']}")


def frasi_fonte(M, fid):
    out = [c["x"] for c in citazioni_tutte(M) if c["f"] == fid]
    E = M.get("eurostar") or {}
    if E and fid == E.get("fonte_tabella"):
        out += [riga_stazione(s) for s in E["stazioni"]]
    return out


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return hashlib.sha256(testo[a:b].encode("utf-8")).hexdigest()[:16]


def file_cache(fid):
    return CACHE / f"{fid}.html"


# Temi ammessi per le citazioni (genera.py li usa per i titoletti delle pagine: un tema sconosciuto non verrebbe mostrato)
TEMI_COMPAGNIE = {"numero", "misure", "extra", "speciali", "cambio", "ice", "altro"}
TEMI_EUROSTAR = {"arrivo", "continente", "ees", "kiosk"}


def controlla_struttura(M):
    """Controlli che prima faceva solo lo script di partenza fuori dal repository: id unici, FAQ che citano id esistenti, temi previsti,
    compagnie lette con tutti i campi, compagnie non lette senza dati."""
    out = []
    ids = [c["id"] for c in citazioni_tutte(M)]
    doppi = sorted({i for i in ids if ids.count(i) > 1})
    if doppi:
        out.append(f"id di citazione doppi: {doppi}")
    for p in M["compagnie"]:
        if not p["letta"]:
            if p.get("citazioni") or p.get("numero") or not p.get("url_provato") or p.get("motivo_tipo") not in ("bloccata", "senza_regola"):
                out.append(f"{p['id']}: compagnia non letta con dati o senza url_provato/motivo_tipo")
            continue
        for k in ("slug", "nome", "nome_titolo", "paese", "treni", "chi", "numero", "misure", "peso", "extra", "speciali", "risposta"):
            if not p.get(k):
                out.append(f"{p['id']}: campo '{k}' mancante")
        mie = {x["id"] for x in p["citazioni"]}
        for x in p["citazioni"]:
            if x["tema"] not in TEMI_COMPAGNIE:
                out.append(f"{p['id']}: citazione {x['id']} con tema non previsto '{x['tema']}'")
        for q in p.get("faq", []):
            if any(i not in mie for i in q["cit"]):
                out.append(f"{p['id']}: FAQ «{q['q']}» cita un id che non c'è")
    E = M.get("eurostar")
    if E:
        mie = {x["id"] for x in E["citazioni"]}
        for x in E["citazioni"]:
            if x["tema"] not in TEMI_EUROSTAR:
                out.append(f"eurostar: citazione {x['id']} con tema non previsto '{x['tema']}'")
        staz = {s["id"] for s in E["stazioni"]}
        for q in E.get("faq", []):
            if q.get("stazione") and q["stazione"] not in staz:
                out.append(f"eurostar: FAQ «{q['q']}» con stazione sconosciuta")
            if any(i not in mie for i in q.get("cit", [])):
                out.append(f"eurostar: FAQ «{q['q']}» cita un id che non c'è")
    return out


def tutte_ricerche(D):
    return {s for g in D["gl"].values() for ss in g.values() for s in ss}


def ricerche_domanda():
    return [m.format(c=c) for c in NOMI_DOMANDA for m in MODELLI_DOMANDA] + EXTRA_DOMANDA


def domanda():
    out = {}
    for gl in GL:
        for q in ricerche_domanda():
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[2].decode("utf-8", "replace"))[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta (nessun nuovo tentativo)
                print(f"  autocompletamento {gl} {q!r}: {e}")
                continue
            out.setdefault(gl, {})[q] = sugg
            time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=us e gl=uk) sui bagagli nei treni per compagnia "
                    "e sugli orari di arrivo Eurostar con l'EES. Ogni domanda delle FAQ delle pagine train-luggage-rules/ e "
                    "eurostar-check-in-times/ è una di queste ricerche (campo 'query' in treni_bagagli_manuali.json). "
                    "Riscritto da raccolta/treni_bagagli.py --domanda.",
           "letto_il": date.today().isoformat(), "ricerche": ricerche_domanda(), "gl": out}
    (DATI / "treni_bagagli_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", len(tutte_ricerche(doc)), "suggerimenti diversi")


def prova_non_lette(M, da_cache, prima):
    """Una richiesta normale per ogni compagnia non letta: codice HTTP e pagina anti-robot sì/no. Nessun aggiramento, nessun nuovo tentativo."""
    out = {}
    for c in M["compagnie"]:
        if c["letta"]:
            continue
        P0 = (prima.get("non_lette") or {}).get(c["id"])
        if da_cache:
            out[c["id"]] = P0 or {"url": c["url_provato"], "http": None, "antirobot": None, "byte": None, "provato_il": None}
            continue
        try:
            stato, finale, raw = leggi(c["url_provato"])
        except urllib.error.HTTPError as e:
            try:
                raw = e.read()
            except Exception:
                raw = b""
            stato, finale = e.code, c["url_provato"]
        except Exception as e:
            stato, finale, raw = 0, c["url_provato"], str(e).encode()
        anti = bool(RX_ANTIROBOT.search(raw[:30000].decode("utf-8", "replace")))
        try:
            car = len(testo_fonte(raw)) if stato == 200 and raw else 0
        except Exception:
            car = 0
        out[c["id"]] = {"url": c["url_provato"], "url_finale": finale, "http": stato, "antirobot": anti, "byte": len(raw), "testo": car,
                        "provato_il": date.today().isoformat()}
        print(f"  non letta {c['id']}: HTTP {stato}{', pagina anti-robot' if anti else ''}, {len(raw)} byte, {car} caratteri di testo")
        time.sleep(0.5)
    return out


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "treni_bagagli_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "treni_bagagli_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "treni_bagagli.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    usate = sorted({c["f"] for c in citazioni_tutte(M)} | ({M["eurostar"]["fonte_tabella"]} if M.get("eurostar") else set()))
    problemi, letture, cambi = controlla_struttura(M), {}, []
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
            raw, stato, finale = f_cache.read_bytes(), P0.get("http", 200), P0.get("url_finale", F["url"])
        else:
            raw, errore = None, None
            for tentativo in range(3):
                try:
                    stato, finale, raw = leggi(F["url"])
                    break
                except urllib.error.HTTPError as e:
                    errore = e  # 403/anti-robot o altro rifiuto del server: NESSUN nuovo tentativo (regola: non aggirare i blocchi)
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
        t = testo_fonte(raw)
        if RX_ANTIROBOT.search(t[:3000]):
            problemi.append(f"{fid}: pagina anti-robot (nessun nuovo tentativo)")
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
                        "lingua": F["lingua"], "letto_il": letto, "cambiato_il": cambiato, "impronta": imp, "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {len(raw)} byte, {len(frasi)} frasi, {len(mancano)} mancanti, impronta {imp}")
        if not da_cache:
            time.sleep(0.5)
    ricerche = tutte_ricerche(D)
    gruppi = [(p["id"], p.get("faq", [])) for p in M["compagnie"]] + [("indice", M.get("faq_indice", []))]
    if M.get("eurostar"):
        gruppi.append(("eurostar", M["eurostar"].get("faq", [])))
    for gid, ff in gruppi:
        for q in ff:
            if q["query"] not in ricerche:
                problemi.append(f"{gid}: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
    if problemi:
        print("NON SCRITTO dati/treni_bagagli.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    non_lette = prova_non_lette(M, da_cache, prima)
    for k, v in non_lette.items():
        c = next(x for x in M["compagnie"] if x["id"] == k)
        if c["motivo_tipo"] == "bloccata" and v.get("http") == 200 and not v.get("antirobot") and (v.get("testo") or 0) >= 1000:
            print(f"  ATTENZIONE: la pagina di {k} ora risponde 200 senza controllo anti-robot: aprirla e, se dice le regole, leggerla a mano")
    doc = {"_nota": "Bagagli sui treni per compagnia e orari di arrivo Eurostar: fatti scritti a mano in dati/treni_bagagli_manuali.json "
                    "(citazioni parola per parola), fonti rilette da raccolta/treni_bagagli.py (HTTP, data di lettura, impronta della zona "
                    "citata); 'non_lette' = esito dell'ultima richiesta alla pagina ufficiale delle compagnie senza pagina (nessun "
                    "aggiramento). Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "non_lette": non_lette,
           "compagnie": M["compagnie"], "faq_indice": M.get("faq_indice", []), "eurostar": M.get("eurostar")}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "treni_bagagli_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    lette = sum(1 for c in M["compagnie"] if c["letta"])
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {lette} compagnie lette, {len(M['compagnie']) - lette} non lette, {len(letture)} fonti"
          + (f", {len(M['eurostar']['stazioni'])} stazioni Eurostar" if M.get("eurostar") else "") + (f", {len(cambi)} cambi" if cambi else ""))


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
