"""Regole del trasporto pubblico per città: come si paga, convalida, multa ufficiale (sezione "public-transport-rules/", blocco "Before you ride").

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/trasporti.py             rilegge le fonti, controlla le frasi citate, scrive dati/trasporti.json
    python3 -I beforeyoufly/raccolta/trasporti.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/trasporti/
    python3 -I beforeyoufly/raccolta/trasporti.py --domanda   rilegge anche l'autocompletamento di Google (dati/trasporti_domanda.json)
    python3 -I beforeyoufly/raccolta/trasporti.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 31/10/2026):
  - Solo fonti ufficiali: l'azienda di trasporto o l'autorità dei trasporti della città (consorzi tariffari come PID, MVV, HVV, ZVV, TFI) o il
    comune. Niente blog, guide turistiche, forum, giornali, rivenditori di biglietti, siti di confronto.
  - I fatti sono scritti a mano in dati/trasporti_manuali.json: ogni frase mostrata sul sito tra virgolette è una citazione parola per parola
    ("citazioni"); le parole nostre (riassunti, risposta, FAQ, traduzioni) le controlla verifica.py (punto 24: nessun numero che non stia in una
    citazione).
  - Una città ha una pagina solo se la multa ufficiale per chi viaggia senza biglietto è letta da una pagina ufficiale attuale. Le altre città
    restano nell'indice come "Not read" con il motivo, senza dati.
  - La lettura vale solo con HTTP 200. NESSUN nuovo tentativo su HTTPError (403, 404, 5xx...): la regola della rete è non aggirare i blocchi
    anti-robot; si riprova solo per errori di rete o di tempo (connessione chiusa, timeout), al massimo 3 volte. Se una fonte non risponde 200 o se
    una citazione non c'è più nel testo normalizzato, lo script NON sovrascrive dati/trasporti.json ed esce con 1: si ricontrolla a mano.
  - Città non lette ("non_lette" nei manuali): per quelle con la pagina bloccata (403, captcha Radware o simili, pagina che si carica solo con
    JavaScript, certificato non verificabile) lo script fa UNA richiesta normale e registra codice, pagina anti-robot sì/no e data. Nessun
    aggiramento: niente browser travestito, niente copie di terzi.
  - Le risposte compresse (gzip) si decomprimono; i PDF si leggono con pdftotext (stesso testo normalizzato delle altre sezioni).
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte; se cambia, il cambio va in dati/trasporti_cambi.json.
  - Pagine grezze in raccolta/.cache/trasporti/ (escluse da git).
  - Ricontrollo: ogni 3 mesi (le multe cambiano spesso a gennaio: rileggere anche a metà gennaio).
"""
import gzip
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
CACHE = Path(__file__).resolve().parent / ".cache" / "trasporti"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# id -> url, ente, titolo della pagina, lingua delle citazioni, tipo (html, pdf)
FONTI = {
    "ath_info": {"url": "https://www.oasa.gr/en/tickets/useful-information/", "ente": "OASA (Athens Urban Transport Organisation)",
                 "titolo": "OASA: Useful information – validation of tickets and cards", "lingua": "en"},
    "ath_fines": {"url": "https://www.oasa.gr/en/passenger-service/information/payment-of-fines/", "ente": "OASA (Athens Urban Transport Organisation)",
                  "titolo": "OASA: Information – payment of fines", "lingua": "en"},
    "bcn_inf": {"url": "https://www.tmb.cat/en/customer-service/user-guide/infringements-statements", "ente": "TMB (Transports Metropolitans de Barcelona)",
                "titolo": "TMB: Offences and appeals", "lingua": "en"},
    "bcn_bank": {"url": "https://www.tmb.cat/en/barcelona-fares-metro-bus/bank-card-validation", "ente": "TMB (Transports Metropolitans de Barcelona)",
                 "titolo": "TMB: Bank card validation", "lingua": "en"},
    "bcn_valid": {"url": "https://www.tmb.cat/en/fares-metro-bus-barcelona/t-mobilitat/how-it-works/how-to-validate", "ente": "TMB (Transports Metropolitans de Barcelona)",
                  "titolo": "TMB: How to validate T-mobilitat", "lingua": "en"},
    "ber_ctrl": {"url": "https://www.bvg.de/en/subscriptions-and-tickets/ticket-control", "ente": "BVG (Berliner Verkehrsbetriebe)",
                 "titolo": "BVG: Ticket control – information about fines and legal rights", "lingua": "en"},
    "ber_faq": {"url": "https://www.bvg.de/en/tourists/faq-tourists", "ente": "BVG (Berliner Verkehrsbetriebe)", "titolo": "BVG: FAQ for tourists", "lingua": "en"},
    "bru_fines": {"url": "https://www.stib-mivb.be/Home/support-client/fines-and-infringements.html", "ente": "STIB-MIVB",
                  "titolo": "STIB-MIVB: Fines and infringements", "lingua": "en"},
    "bru_bank": {"url": "https://www.stib-mivb.be/buy/your-bank-card-is-your-ticket", "ente": "STIB-MIVB",
                 "titolo": "STIB-MIVB: Your bank card is your ticket", "lingua": "en"},
    "bud_pen": {"url": "https://bkk.hu/en/tickets-and-passes/information-about-penalty-fares/general-information/", "ente": "BKK (Centre for Budapest Transport)",
                "titolo": "BKK: Penalty fare – general information", "lingua": "en"},
    "bud_valid": {"url": "https://bkk.hu/en/tickets-and-passes/validation-of-paper-tickets/", "ente": "BKK (Centre for Budapest Transport)",
                  "titolo": "BKK: Guide for tourists on how to use tickets, travelcards and passes", "lingua": "en"},
    "bud_news": {"url": "https://bkk.hu/en/news/2026/04/buy-and-validate-your-single-ticket-with-a-single-tap.16407/", "ente": "BKK (Centre for Budapest Transport)",
                 "titolo": "BKK news, 22 April 2026: Buy and validate your single ticket with a single tap", "lingua": "en"},
    "bud_nov": {"url": "https://bkk.hu/en/news/2026/10/ticket-validation-has-become-simpler-on-bkks-lines-in-street-level-transport.17477/",
                "ente": "BKK (Centre for Budapest Transport)",
                "titolo": "BKK news, 29 October 2026: Ticket validation has become simpler on BKK’s lines in street-level transport", "lingua": "en"},
    "dub_fare": {"url": "https://www.transportforireland.ie/fares/fare-evasion-on-tfi-services/", "ente": "Transport for Ireland (National Transport Authority)",
                 "titolo": "TFI: Fare evasion on TFI services", "lingua": "en"},
    "dub_luas": {"url": "https://www.transportforireland.ie/fares/luas-fares/", "ente": "Transport for Ireland (National Transport Authority)",
                 "titolo": "TFI: Luas tram fare info", "lingua": "en"},
    "edi_tap": {"url": "https://edinburghtrams.com/tap-tap", "ente": "Edinburgh Trams", "titolo": "Edinburgh Trams: Tap On, Tap Off", "lingua": "en"},
    "edi_cond": {"url": "https://edinburghtrams.com/contactless-payment-cards-conditions-use", "ente": "Edinburgh Trams",
                 "titolo": "Edinburgh Trams: Contactless payment cards – conditions of use", "lingua": "en"},
    "gva_good": {"url": "https://www.tpg.ch/en/travel-good-standing", "ente": "tpg (Transports publics genevois)", "titolo": "tpg: Travel in good standing", "lingua": "en"},
    "ham_tarif": {"url": "https://www.hvv.de/resource/blob/2384/80b8c14227b0bea5dbfbf7c9e44d2b94/hvv_tarif_gemeinschaftstarif_befoerderungsbedingungen.pdf",
                  "ente": "hvv (Hamburger Verkehrsverbund)", "titolo": "hvv Gemeinschaftstarif, valid from 1 October 2026 (PDF)", "lingua": "de", "tipo": "pdf"},
    "lis_legal": {"url": "https://www.metrolisboa.pt/en/travel/legal-information/", "ente": "Metropolitano de Lisboa", "titolo": "Metro Lisboa: Legal information", "lingua": "en"},
    "lis_bank": {"url": "https://www.metrolisboa.pt/en/metro-bank-card/", "ente": "Metropolitano de Lisboa", "titolo": "Metro Lisboa: Metro + bank card", "lingua": "en"},
    "mad_sur": {"url": "https://www.metromadrid.es/en/surcharge", "ente": "Metro de Madrid", "titolo": "Metro de Madrid: Extraordinary travel card top-up", "lingua": "en"},
    "mad_emv": {"url": "https://www.metromadrid.es/en/travel-in-the-metro/passenger-regulations/rules-for-the-use-of-emv-compliant-contactless-bank-cards",
                "ente": "Metro de Madrid", "titolo": "Metro de Madrid: Rules for the use of EMV-compliant contactless bank cards", "lingua": "en"},
    "mil_cless": {"url": "https://www.atm.it/en/ViaggiaConNoi/Biglietti/Pages/contactless_cards_metro.aspx", "ente": "ATM (Azienda Trasporti Milanesi)",
                  "titolo": "ATM: Contactless pay as you go", "lingua": "en"},
    "mil_sanz": {"url": "https://www.atm.it/it/ViaggiaConNoi/Abbonamenti/Documents/Sanzioni_ATM.pdf", "ente": "ATM (Azienda Trasporti Milanesi)",
                 "titolo": "ATM: Sanzioni amministrative dal 09/01/2023 (PDF)", "lingua": "it", "tipo": "pdf"},
    "mil_guida": {"url": "https://www.atm.it/it/ViaggiaConNoi/Guide/Pagine/Usarebigliettieabbonamenti.aspx", "ente": "ATM (Azienda Trasporti Milanesi)",
                  "titolo": "ATM: Usare biglietti e abbonamenti (guide)", "lingua": "it"},
    "mil_mi34": {"url": "https://nuovosistematariffario.atm.it/static/tariffe/mi3-mi4/index.html", "ente": "ATM (Azienda Trasporti Milanesi)",
                 "titolo": "ATM fare finder (STIBM): Mi3 – Mi4 tickets and passes", "lingua": "it"},
    "mtl_fares": {"url": "https://www.stm.info/en/fares-pricing", "ente": "STM (Société de transport de Montréal)", "titolo": "STM: Fares and pricing", "lingua": "en"},
    "mtl_1trip": {"url": "https://www.stm.info/en/info/fares/transit-fares/1-trip", "ente": "STM (Société de transport de Montréal)", "titolo": "STM: 1-trip, All modes A", "lingua": "en"},
    "muc_ebe": {"url": "https://www.mvg.de/services/ebe.html?lang=en", "ente": "MVG (Münchner Verkehrsgesellschaft)", "titolo": "MVG: Erhöhtes Beförderungsentgelt", "lingua": "de"},
    "osl_ctrl": {"url": "https://ruter.no/en/about-our-tickets/ticket-control", "ente": "Ruter", "titolo": "Ruter: Ticket inspections", "lingua": "en"},
    "osl_single": {"url": "https://ruter.no/en/about-our-tickets/single-ticket", "ente": "Ruter", "titolo": "Ruter: Single ticket", "lingua": "en"},
    "prg_sur": {"url": "https://www.dpp.cz/en/fares/penalties-transport-inspectors/surcharge-amount", "ente": "DPP (Prague Public Transit Company)",
                "titolo": "DPP: Surcharge amount", "lingua": "en"},
    "prg_tarif": {"url": "https://pid.cz/en/new-pid-tariff-from-1-january-2026-dont-pay-more-than-you-have-to/", "ente": "PID (Prague Integrated Transport)",
                  "titolo": "PID: New PID tariff from 1 January 2026", "lingua": "en"},
    "prg_cash": {"url": "https://www.dpp.cz/en/fares/cashless-payment-of-fare", "ente": "DPP (Prague Public Transit Company)", "titolo": "DPP: Cashless payment of fare", "lingua": "en"},
    "tor_pop": {"url": "https://www.ttc.ca/Fares-and-passes/Proof-of-Payment-and-fare-inspection", "ente": "TTC (Toronto Transit Commission)",
                "titolo": "TTC: Proof-of-Payment and fare inspection", "lingua": "en"},
    "van_enf": {"url": "https://www.translink.ca/transit-fares/fare-enforcement", "ente": "TransLink", "titolo": "TransLink: Fare enforcement", "lingua": "en"},
    "van_inf": {"url": "https://www.translink.ca/transit-fares/fare-infraction", "ente": "TransLink", "titolo": "TransLink: Fare infraction", "lingua": "en"},
    "zrh_pen": {"url": "https://www.zvv.ch/en/travelcards-and-tickets/sales-and-support/ticket-inspection/penalty-fares.html", "ente": "ZVV (Zürcher Verkehrsverbund)",
                "titolo": "ZVV: Penalty fares in the ZVV region", "lingua": "en"},
    "zrh_insp": {"url": "https://www.zvv.ch/en/travelcards-and-tickets/sales-and-support/ticket-inspection/inspection.html", "ente": "ZVV (Zürcher Verkehrsverbund)",
                 "titolo": "ZVV: Ticket inspection", "lingua": "en"},
}
RX_ANTIROBOT = re.compile(r"Just a moment|_Incapsula_Resource|perfdrive\.com|Radware|Attention Required|cf-browser-verification|captcha", re.I)

# Città cercate dall'autocompletamento (nome usato nelle ricerche)
CITTA_DOMANDA = ["rome", "paris", "london", "berlin", "prague", "budapest", "amsterdam", "barcelona", "lisbon", "milan", "vienna", "dublin",
                 "munich", "hamburg", "athens", "oslo", "brussels", "copenhagen", "madrid", "zurich", "geneva", "edinburgh", "stockholm",
                 "helsinki", "warsaw", "krakow", "florence", "venice", "naples", "turin", "bologna", "porto", "valencia", "lyon", "riga",
                 "new york", "toronto", "montreal", "vancouver", "sydney"]
MODELLI_DOMANDA = ["{c} metro fine", "{c} public transport fine", "fine for no ticket {c}", "{c} metro contactless",
                   "how to pay for metro in {c}", "do you need to validate ticket in {c}", "{c} bus ticket validation"]
EXTRA_DOMANDA = ["public transport fines", "fine for not validating ticket", "contactless payment metro", "can i use contactless on",
                 "do you need to validate", "fine for no ticket"]
GL = ("us", "uk")


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html,application/pdf"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        return r.status, r.geturl(), (gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def testo_html(html_):
    """Testo visibile normalizzato (come raccolta/patente_straniera.py)."""
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
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    if tipo == "pdf" or raw[:4] == b"%PDF":
        return testo_pdf(raw)
    return testo_html(raw.decode("utf-8", "replace"))


def frasi_fonte(M, fid):
    return [c["x"] for p in M["citta"] for c in p.get("citazioni", []) if c["f"] == fid]


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


def ricerche_domanda():
    return [m.format(c=c) for c in CITTA_DOMANDA for m in MODELLI_DOMANDA] + EXTRA_DOMANDA


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
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=us e gl=uk) sulle regole del trasporto pubblico "
                    "per città (multa, contactless, convalida). Ogni domanda delle FAQ della sezione public-transport-rules/ è una di queste "
                    "ricerche (campo 'query' in trasporti_manuali.json). Riscritto da raccolta/trasporti.py --domanda.",
           "letto_il": date.today().isoformat(), "ricerche": ricerche_domanda(), "gl": out}
    (DATI / "trasporti_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", len(tutte_ricerche(doc)), "suggerimenti diversi")


def prova_non_lette(M, da_cache, prima):
    """Una richiesta normale per ogni città non letta: codice HTTP e se la risposta è una pagina anti-robot. Nessun aggiramento, nessun nuovo
    tentativo. Serve a sapere quando una pagina torna leggibile (allora si legge a mano e la città passa tra quelle con pagina)."""
    out = {}
    for c in M["citta"]:
        if c["letta"]:
            continue
        P0 = (prima.get("non_lette") or {}).get(c["id"])
        if da_cache:
            out[c["id"]] = P0 or {"url": c["url_provato"], "http": None, "antirobot": None, "byte": None, "provato_il": None}
            continue
        try:
            stato, finale, raw = leggi(c["url_provato"])
        except urllib.error.HTTPError as e:
            stato, finale, raw = e.code, c["url_provato"], b""
        except Exception as e:
            stato, finale, raw = 0, c["url_provato"], str(e).encode()
        anti = bool(RX_ANTIROBOT.search(raw[:30000].decode("utf-8", "replace"))) or "perfdrive" in (finale or "")
        try:
            car = len(testo_fonte(raw)) if stato == 200 and raw else 0
        except Exception:
            car = 0
        out[c["id"]] = {"url": c["url_provato"], "http": stato, "antirobot": anti, "byte": len(raw), "testo": car,
                        "provato_il": date.today().isoformat()}
        print(f"  non letta {c['id']}: HTTP {stato}{', pagina anti-robot' if anti else ''}, {len(raw)} byte, {car} caratteri di testo")
        time.sleep(0.5)
    return out


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "trasporti_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "trasporti_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "trasporti.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    usate = sorted({c["f"] for p in M["citta"] for c in p.get("citazioni", [])})
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
                        "lingua": F["lingua"], "tipo": F.get("tipo", "html"), "letto_il": letto, "cambiato_il": cambiato, "impronta": imp,
                        "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {len(raw)} byte, {len(frasi)} frasi, {len(mancano)} mancanti, impronta {imp}")
        if not da_cache:
            time.sleep(0.4)
    ricerche = tutte_ricerche(D)
    for p in M["citta"]:
        for q in p.get("faq", []):
            if q["query"] not in ricerche:
                problemi.append(f"{p['id']}: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
    for q in M.get("faq_indice", []):
        if q["query"] not in ricerche:
            problemi.append(f"indice: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
    if problemi:
        print("NON SCRITTO dati/trasporti.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    non_lette = prova_non_lette(M, da_cache, prima)
    tornate = [k for k, v in non_lette.items() if v.get("http") == 200 and not v.get("antirobot") and (v.get("testo") or 0) >= 1000
               and next(c for c in M["citta"] if c["id"] == k)["motivo_tipo"] == "bloccata"]
    for k in tornate:
        print(f"  ATTENZIONE: la pagina di {k} ora risponde 200 senza controllo anti-robot: aprirla e, se dice la multa, leggerla a mano")
    doc = {"_nota": "Regole del trasporto pubblico per città: fatti scritti a mano in dati/trasporti_manuali.json (citazioni parola per parola), "
                    "fonti rilette da raccolta/trasporti.py (HTTP, data di lettura, impronta della zona citata); 'non_lette' = esito dell'ultima "
                    "richiesta alla pagina ufficiale delle città senza pagina (nessun aggiramento). Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "non_lette": non_lette,
           "citta": M["citta"], "faq_indice": M.get("faq_indice", [])}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "trasporti_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    lette = sum(1 for c in M["citta"] if c["letta"])
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {lette} città lette, {len(M['citta']) - lette} non lette, {len(letture)} fonti"
          + (f", {len(cambi)} cambi" if cambi else ""))


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
