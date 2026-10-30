"""Pedaggi con l'auto a noleggio (sezione "Tolls with a rental car"): rilegge le fonti ufficiali e segnala i cambi.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/pedaggi.py             rilegge le fonti, controlla le frasi citate, scrive dati/pedaggi.json
    python3 -I beforeyoufly/raccolta/pedaggi.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/pedaggi/
    python3 -I beforeyoufly/raccolta/pedaggi.py --domanda   rilegge anche l'autocompletamento di Google (dati/pedaggi_domanda.json)
    python3 -I beforeyoufly/raccolta/pedaggi.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 30/10/2026):
  - Solo fonti ufficiali: il gestore delle autostrade o del sistema di pedaggio, o il governo (elenco in FONTI). Niente siti di
    rivenditori, niente pagine delle compagnie di noleggio (dal server rispondono 403/404 o si caricano in JavaScript).
  - I fatti sono scritti a mano in dati/pedaggi_manuali.json: ogni frase mostrata sul sito è una citazione parola per parola
    ("citazioni") e ogni prezzo ha la sua "prova", un pezzo di testo della fonte che contiene la cifra. Nessun prezzo senza fonte.
  - La lettura vale solo con HTTP 200. Se una fonte non risponde 200, o se una citazione o una prova non c'è più nel testo
    normalizzato, lo script NON sovrascrive dati/pedaggi.json ed esce con 1: si ricontrolla a mano.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte: il testo normalizzato dall'inizio della prima frase citata alla
    fine dell'ultima. Se cambia, il cambio va in dati/pedaggi_cambi.json (la pagina intorno alle citazioni è cambiata: rileggerla).
  - Ungheria: il sito nemzetiutdij.hu si carica in JavaScript; si legge l'API pubblica che usa la pagina stessa (stesso contenuto).
  - Pagine grezze in raccolta/.cache/pedaggi/ (escluse da git).
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
CACHE = Path(__file__).resolve().parent / ".cache" / "pedaggi"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
HU_API = "https://nemzetiutdij.hu/cms/api/public/nemzetiutdij/contents/menuitem/"

# id -> url letto, pagina da mostrare ai lettori (se diversa), ente, titolo della pagina, lingua, tipo (html o api_hu)
FONTI = {
    "pt_home": {"url": "https://www.pttolls.com/en/", "ente": "Infraestruturas de Portugal", "titolo": "PT Tolls (Infraestruturas de Portugal): toll systems and how to pay"},
    "pt_faq": {"url": "https://www.pttolls.com/en/faq-frequently-asked-questions", "ente": "Infraestruturas de Portugal", "titolo": "PT Tolls: FAQ – Frequently Asked Questions – Tolls"},
    "ie_eflow": {"url": "https://www.eflow.ie/how-it-works", "ente": "eFlow (Transport Infrastructure Ireland)", "titolo": "eFlow: About the M50 Toll Road"},
    "ie_tii": {"url": "https://www.tii.ie/en/roads-tolling/tolling-information/toll-locations-and-charges/m50-barrier-free-tolling/",
               "ente": "Transport Infrastructure Ireland", "titolo": "TII: M50 Barrier Free Tolling (toll locations and charges)"},
    "no_payment": {"url": "https://www.autopass.no/en/user/payment/", "ente": "AutoPASS (Norwegian Public Roads Administration)", "titolo": "AutoPASS: Payment"},
    "no_system": {"url": "https://www.autopass.no/en/user/the-road-toll-system/", "ente": "AutoPASS (Norwegian Public Roads Administration)", "titolo": "AutoPASS: The road toll system"},
    "no_rates": {"url": "https://www.autopass.no/en/user/rates-and-discounts/", "ente": "AutoPASS (Norwegian Public Roads Administration)", "titolo": "AutoPASS: Rates and discounts"},
    "it_cash": {"url": "https://www.autostrade.it/en/servizi-al-cliente/pedaggio/metodi-di-pagamento/contanti", "ente": "Autostrade per l'Italia", "titolo": "Autostrade per l'Italia: Payment methods – Cash"},
    "it_cards": {"url": "https://www.autostrade.it/en/servizi-al-cliente/pedaggio/metodi-di-pagamento/carte", "ente": "Autostrade per l'Italia", "titolo": "Autostrade per l'Italia: Payment methods – Credit card"},
    "it_unpaid": {"url": "https://www.autostrade.it/en/servizi-al-cliente/pedaggio/mancato-pagamento/paga-online", "ente": "Autostrade per l'Italia", "titolo": "Autostrade per l'Italia: Unpaid toll – Pay online"},
    "fr_aliae": {"url": "https://www.aliae.com/en", "ente": "ALIAE (A79 motorway concession, APRR group)", "titolo": "ALIAE: the A79 motorway"},
    "fr_aprr": {"url": "https://peagereinvente.aprr.fr/", "ente": "APRR", "titolo": "APRR: Flux libre sur ALIAE et entrées sans tickets sur AREA", "lingua": "fr"},
    "fr_aprr_oubli": {"url": "https://peagereinvente.aprr.fr/peage-en-flux-libre-que-faire-si-joublie-de-payer.html", "ente": "APRR",
                      "titolo": "APRR: Péage en flux libre : que faire si j’oublie de payer ?", "lingua": "fr"},
    "es_tarifas": {"url": "https://www.autopistas.com/es/beneficios/tarifas-y-descuentos", "ente": "Autopistas (Abertis)", "titolo": "Autopistas (Abertis): Tarifas y descuentos", "lingua": "es"},
    "es_viat": {"url": "https://www.autopistas.com/es/beneficios/servicios/via-t", "ente": "Autopistas (Abertis)", "titolo": "Autopistas (Abertis): Vía T", "lingua": "es"},
    "hr_toll": {"url": "https://www.hac.hr/en/toll", "ente": "Hrvatske autoceste (HAC)", "titolo": "Hrvatske autoceste: Toll"},
    "hr_faq": {"url": "https://www.hac.hr/en/toll/faq", "ente": "Hrvatske autoceste (HAC)", "titolo": "Hrvatske autoceste: Toll FAQ"},
    "gr_aodos": {"url": "https://www.aodos.gr/en/diodia-e-pass/tolls/", "ente": "Attiki Odos", "titolo": "Attiki Odos (Attica Tollway): Tolls"},
    "at_help": {"url": "https://help.asfinag.at/en/vignette-and-section-tolls/", "ente": "ASFINAG", "titolo": "ASFINAG help: Vignette and section tolls"},
    "at_vignette": {"url": "https://shop.asfinag.at/en/products/digital-vignette/", "ente": "ASFINAG", "titolo": "ASFINAG toll shop: Digital vignette"},
    "at_prezzi": {"url": "https://shop.asfinag.at/en/toll-products/digital-vignette/?type=Car", "ente": "ASFINAG", "titolo": "ASFINAG toll shop: Digital Vignette for cars"},
    "ch_main": {"url": "https://www.bazg.admin.ch/en/motorway-charge-vignette", "ente": "Federal Office for Customs and Border Security (FOCBS)", "titolo": "FOCBS: Motorway charge (vignette)"},
    "ch_faq": {"url": "https://www.bazg.admin.ch/en/faq-vignette-and-e-vignette-purchase", "ente": "Federal Office for Customs and Border Security (FOCBS)", "titolo": "FOCBS: FAQ vignette and e-vignette purchase"},
    "ch_evignette": {"url": "https://www.bazg.admin.ch/en/electronic-vignette-via-portal-purchase", "ente": "Federal Office for Customs and Border Security (FOCBS)", "titolo": "FOCBS: Electronic vignette (Via portal)"},
    "si_gov": {"url": "https://www.gov.si/en/topics/tolls/", "ente": "Government of Slovenia (Ministry of Infrastructure and Energy)", "titolo": "GOV.SI: Tolls"},
    "si_asfinag": {"url": "https://shop.asfinag.at/en/products/slovenian-e-vignette/", "ente": "ASFINAG", "titolo": "ASFINAG toll shop: Slovenian e-vignette"},
    "cz_home": {"url": "https://edalnice.gov.cz/en", "ente": "State Fund for Transport Infrastructure (eDalnice.gov.cz)", "titolo": "eDalnice.gov.cz: Electronic Vignette – official state e-shop"},
    "cz_prezzi": {"url": "https://edalnice.gov.cz/en/price-list", "ente": "State Fund for Transport Infrastructure (eDalnice.gov.cz)", "titolo": "eDalnice.gov.cz: Price list"},
    "cz_multe": {"url": "https://edalnice.gov.cz/en/inspection-and-fines", "ente": "State Fund for Transport Infrastructure (eDalnice.gov.cz)", "titolo": "eDalnice.gov.cz: Inspection and fines"},
    "hu_prezzi": {"url": HU_API + "61851d44b77430003c3cb87a", "pagina": "https://nemzetiutdij.hu/en/e-vignette/tolls/e-vignette-rates",
                  "ente": "National Toll Payment Services (Nemzeti Útdíjfizetési Szolgáltató)", "titolo": "Nemzeti Útdíjfizetési Szolgáltató: E-vignette rates", "tipo": "api_hu"},
    "hu_multe": {"url": HU_API + "6a01d0a9ca5a4e0013642a71", "pagina": "https://nemzetiutdij.hu/en/e-vignette/surcharges/surcharge-differential-surcharge",
                 "ente": "National Toll Payment Services (Nemzeti Útdíjfizetési Szolgáltató)", "titolo": "Nemzeti Útdíjfizetési Szolgáltató: Surcharge, differential surcharge", "tipo": "api_hu"},
}

# Ricerche da rileggere con --domanda (autocompletamento, client=firefox, hl=en, gl=us e gl=uk)
DOMANDA_PAESI = {"PT": "portugal", "IE": "ireland", "NO": "norway", "IT": "italy", "FR": "france", "ES": "spain", "AT": "austria", "CH": "switzerland",
                 "SI": "slovenia", "CZ": "czech republic", "HU": "hungary", "HR": "croatia", "GR": "greece"}
DOMANDA_MODELLI = ["{p} tolls rental car", "{p} tolls hire car", "tolls in {p} rental car", "{p} toll roads rental car", "{p} vignette rental car",
                   "how to pay tolls in {p}", "{p} tolls"]
DOMANDA_EXTRA = ["m50 toll rental car", "m50 toll hire car", "autopass rental car", "portugal electronic tolls rental car", "italy telepass rental car",
                 "austria vignette hire car", "swiss vignette rental car"]


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html,application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read().decode("utf-8", "replace")


def testo_html(html_):
    """Testo visibile normalizzato: niente script e stili, tag "in linea" tolti senza spazio, spazi unificati, niente spazio prima della punteggiatura."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ").replace("​", "").replace("⁣", "").replace("﻿", "")
    t = re.sub(r"\s+", " ", t)
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_fonte(raw, tipo="html"):
    if tipo == "api_hu":
        d = json.loads(raw)
        return testo_html(" ".join((c.get("title") or "") + " " + (c.get("contentBody") or "") for c in d))
    return testo_html(raw)


def frasi_fonte(M, fid):
    """Tutti i testi che dati/pedaggi_manuali.json cita da una fonte (citazioni dei Paesi e prove dei prezzi)."""
    out = []
    for p in M["paesi"]:
        for c in p["citazioni"]:
            if c["f"] == fid:
                out.append(c["x"])
        for pr in p.get("prezzi", []):
            if pr["f"] == fid:
                out.append(pr["prova"])
    return out


def impronta_zona(testo, frasi):
    """Impronta del testo dalla prima alla ultima frase citata (None se una frase manca)."""
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return hashlib.sha256(testo[a:b].encode("utf-8")).hexdigest()[:16]


def domanda():
    out = {}
    for gl in ("us", "uk"):
        query = [(c, m.format(p=p)) for c, p in DOMANDA_PAESI.items() for m in DOMANDA_MODELLI] + [("_extra", q) for q in DOMANDA_EXTRA]
        for c, q in query:
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[2])[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta
                print(f"  autocompletamento {gl} {q!r}: {e}")
                continue
            out.setdefault(c, {}).setdefault(gl, {})[q] = sugg
            time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=us e gl=uk) sui pedaggi con l'auto a noleggio. "
                    "Ogni domanda delle FAQ della sezione tolls-rental-car/ deve essere una di queste ricerche (campo 'query' in pedaggi_manuali.json). "
                    "Riscritto da raccolta/pedaggi.py --domanda.",
           "letto_il": date.today().isoformat(), "modelli": DOMANDA_MODELLI, "extra": DOMANDA_EXTRA, "paesi": out}
    (DATI / "pedaggi_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", {c: sum(len(v) for g in d.values() for v in g.values()) for c, d in out.items()})


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "pedaggi_manuali.json").read_text(encoding="utf-8"))
    f_dati = DATI / "pedaggi.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    usate = sorted({c["f"] for p in M["paesi"] for c in p["citazioni"]} | {pr["f"] for p in M["paesi"] for pr in p.get("prezzi", [])})
    problemi, letture, cambi = [], {}, []
    for fid in usate:
        F = FONTI.get(fid)
        if not F:
            problemi.append(f"fonte {fid} non in FONTI")
            continue
        tipo = F.get("tipo", "html")
        f_cache = CACHE / f"{fid}.{'json' if tipo == 'api_hu' else 'html'}"
        if da_cache:
            if not f_cache.exists():
                problemi.append(f"{fid}: nessuna copia in cache")
                continue
            raw, stato, finale = f_cache.read_text(encoding="utf-8"), (prima["fonti"].get(fid) or {}).get("http"), (prima["fonti"].get(fid) or {}).get("url_finale")
        else:
            raw = None
            for tentativo in range(5):  # alcuni siti (help.asfinag.at) rispondono 403 a intermittenza: si riprova con pause crescenti
                try:
                    stato, finale, raw = leggi(F["url"])
                    break
                except Exception as e:
                    errore = e
                    time.sleep(5 + 10 * tentativo)
            if raw is None:
                problemi.append(f"{fid}: lettura fallita ({errore})")
                continue
            f_cache.write_text(raw, encoding="utf-8")
        if stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
        t = testo_fonte(raw, tipo)
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
        letture[fid] = {"url": F["url"], "pagina": F.get("pagina", F["url"]), "url_finale": finale, "http": stato, "byte": len(raw.encode("utf-8")),
                        "ente": F["ente"], "titolo": F["titolo"], "lingua": F.get("lingua", "en"), "letto_il": letto, "cambiato_il": cambiato,
                        "impronta": imp, "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {letture[fid]['byte']} byte, {len(frasi)} frasi, {len(mancano)} mancanti, impronta {imp}")
    if problemi:
        print("NON SCRITTO dati/pedaggi.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    doc = {"_nota": "Pedaggi con l'auto a noleggio: fatti scritti a mano in dati/pedaggi_manuali.json (citazioni parola per parola e prove dei prezzi), "
                    "fonti rilette da raccolta/pedaggi.py (HTTP, data di lettura, impronta della zona citata). Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "paesi": M["paesi"]}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "pedaggi_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(M['paesi'])} Paesi, {len(letture)} fonti" + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        F = FONTI[fid]
        f_cache = CACHE / f"{fid}.{'json' if F.get('tipo') == 'api_hu' else 'html'}"
        if not f_cache.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_cache.write_text(leggi(F["url"])[2], encoding="utf-8")
        print(testo_fonte(f_cache.read_text(encoding="utf-8"), F.get("tipo", "html")))
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda()
    main()
