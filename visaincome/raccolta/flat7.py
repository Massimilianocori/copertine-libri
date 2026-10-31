"""Legge le fonti ufficiali sull'imposta sostitutiva del 7% per i pensionati esteri (art. 24-ter TUIR, dal 1/1/2027 art. 247
del nuovo testo unico, D.Lgs. 117/2026) e la popolazione ISTAT di tutti i Comuni; scrive visaincome/dati/flat7.json
(pagine "Italy 7% flat tax for foreign pensioners" del sito, dal 31/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/flat7.py              # rilegge le fonti e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/flat7.py --domanda    # rifà anche l'autocompletamento di Google (gl=us e gb)

Fonti (lette A MANO il 31/10/2026; ogni regola ha il FRAMMENTO del testo ufficiale da cui viene)
- Normattiva: art. 24-ter TUIR vigente (testo in vigore dal 7/4/2026 al 31/12/2026, soglia 30.000), lo stesso articolo al
  1/1/2027 (abrogato dal D.Lgs. 117/2026), L. 11/3/2026 n. 34 art. 26 (20.000 → 30.000), D.Lgs. 19/6/2026 n. 117 art. 247
  (stessa regola dal 2027, versione in vigore dal 7/8/2026 con 30.000) e art. 377 (decorrenza 1/1/2027), allegati 1, 2 e 2-bis
  al D.L. 189/2016 (Comuni del sisma 2016-2017). Gli articoli del D.Lgs. 117 e gli allegati si leggono solo dopo aver aperto la
  pagina dell'atto (cookie di sessione): lo script lo fa.
- Agenzia delle Entrate: scheda "Regime opzionale per i pensionati esteri - Che cos'è" (aggiornata l'8/5/2026: 30mila dal
  7/4/2026, popolazione ISTAT al 1° gennaio dell'anno precedente) e circolare 21/E del 17/7/2020 (anno della popolazione,
  10 anni in tutto, accordi di cooperazione amministrativa). La circolare è del 2020 e cita ancora i limiti di allora
  (20.000 e 3.000 per i Comuni del sisma): la usiamo solo per l'anno della popolazione e la durata.
- Regione Abruzzo, BURA 2017, Allegato B1 "Elenco dei comuni nell'area cratere" (sisma del 6/4/2009: 57 Comuni, tutti in Abruzzo).
- ISTAT: popolazione residente al 1° gennaio 2025 e 2026 (stima) per Comune (demo.istat.it, POSAS, riga "999" = totale),
  elenco dei Comuni (codici, regione, sigla) ed elenco dei Comuni soppressi (fusioni del 2017 dei Comuni degli allegati).

Regole
- Se un frammento non è più nel testo, la fonte è cambiata: il JSON NON viene aggiornato (esce con codice 1) finché qualcuno non
  rilegge la fonte e aggiorna LETTURE. Ogni nome degli allegati deve corrispondere a un Comune ISTAT (direttamente, con ALIAS o
  con FUSIONI confermate dall'elenco dei soppressi); i tre file ISTAT devono avere gli stessi codici.
- Il sito NON dice che un Comune "qualifica": dice solo se la popolazione ISTAT dell'anno giusto è entro 30.000 e se il Comune
  è in una delle aree della legge. Decide l'Agenzia delle Entrate, e servono gli altri requisiti.
- I file grezzi ISTAT vanno in raccolta/_grezzi/flat7/ (fuori da git).
"""
import csv
import hashlib
import html as H
import http.cookiejar
import io
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "flat7.json"
GREZZI = RADICE / "raccolta" / "_grezzi" / "flat7"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

N = "https://www.normattiva.it/uri-res/N2Ls?"
ATTO_117 = N + "urn:nir:stato:decreto.legislativo:2026-06-19;117"
ATTO_189 = N + "urn:nir:stato:decreto.legge:2016-10-17;189"
ART = ("https://www.normattiva.it/atto/caricaArticolo?art.versione={v}&art.idGruppo={g}&art.flagTipoArticolo={t}&art.codiceRedazionale={c}"
       "&art.idArticolo={a}&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta={d}&art.progressivo=0&")

FONTI = {
    "art24ter": {"url": N + "urn:nir:presidente.repubblica:decreto:1986-12-22;917~art24ter!vig=", "editore": "Normattiva",
                 "titolo": "Income Tax Code (TUIR, Presidential Decree 917/1986), article 24-ter, text in force"},
    "art24ter_2027": {"url": N + "urn:nir:presidente.repubblica:decreto:1986-12-22;917~art24ter!vig=2027-01-01", "editore": "Normattiva",
                      "titolo": "TUIR article 24-ter, text at 1 January 2027 (repealed by Legislative Decree 117/2026)"},
    "l34": {"url": N + "urn:nir:stato:legge:2026-03-11;34~art26", "editore": "Normattiva",
            "titolo": "Law no. 34 of 11 March 2026, article 26 (limit raised from 20,000 to 30,000 inhabitants)"},
    "art247": {"url": ART.format(v=2, g=46, t=1, c="26G00131", a=247, d="2026-07-03"), "link": ATTO_117, "cookie": True, "editore": "Normattiva",
               "titolo": "Legislative Decree no. 117 of 19 June 2026 (new income tax code), article 247"},
    "art377": {"url": ART.format(v=1, g=74, t=1, c="26G00131", a=377, d="2026-07-03"), "link": ATTO_117, "cookie": True, "editore": "Normattiva",
               "titolo": "Legislative Decree no. 117 of 19 June 2026, article 377 (in force from 1 January 2027)"},
    "all1": {"url": ART.format(v=1, g=15, t=1, c="16G00205", a=1, d="2016-10-18"), "link": ATTO_189, "cookie": True, "editore": "Normattiva",
             "titolo": "Decree-Law 189/2016, Annex 1 (towns hit by the earthquake of 24 August 2016)"},
    "all2": {"url": ART.format(v=1, g=15, t=2, c="16G00205", a=1, d="2016-10-18"), "link": ATTO_189, "cookie": True, "editore": "Normattiva",
             "titolo": "Decree-Law 189/2016, Annex 2 (earthquakes of 26 and 30 October 2016)"},
    "all2bis": {"url": ART.format(v=1, g=15, t=3, c="16G00205", a=1, d="2016-10-18"), "link": ATTO_189, "cookie": True, "editore": "Normattiva",
                "titolo": "Decree-Law 189/2016, Annex 2-bis (earthquake of 18 January 2017)"},
    "ade": {"url": "https://www.agenziaentrate.gov.it/portale/schede/agevolazioni/regime-opzionale-per-i-pensionati-esteri-che-cose-cittadini",
            "editore": "Agenzia delle Entrate", "titolo": "Regime opzionale per i pensionati esteri: che cos'è (updated 8 May 2026)", "data": "2026-05-08"},
    "circ21e": {"url": "https://www.agenziaentrate.gov.it/portale/documents/20143/0/Circolare+n.+21E+del+17.07.2020.pdf/96191701-87ef-ce63-e163-a8a6e37e64ad",
                "editore": "Agenzia delle Entrate", "titolo": "Circular 21/E of 17 July 2020", "data": "2020-07-17"},
    "bura2009": {"url": "https://bura.regione.abruzzo.it/sites/bura.regione.abruzzo.it/archivio_bura/2017/Allegati/Spe_50_Doc0_3.pdf",
                 "editore": "Regione Abruzzo (BURA)", "titolo": "Annex B1: towns in the crater of the 6 April 2009 earthquake"},
    "istat2025": {"url": "https://demo.istat.it/data/posas/POSAS_2025_it_Comuni.zip", "editore": "ISTAT",
                  "titolo": "Resident population by municipality on 1 January 2025", "grezzo": "POSAS_2025_it_Comuni.zip"},
    "istat2026": {"url": "https://demo.istat.it/data/posas/POSAS_2026_it_Comuni.zip", "editore": "ISTAT",
                  "titolo": "Resident population by municipality on 1 January 2026 (estimate)", "grezzo": "POSAS_2026_it_Comuni.zip"},
    "elenco": {"url": "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv", "editore": "ISTAT",
               "titolo": "List of Italian municipalities (codes, regions, provinces)", "grezzo": "Elenco-comuni-italiani.csv"},
    "soppressi": {"url": "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-soppressi.zip", "editore": "ISTAT",
                  "titolo": "List of suppressed municipalities (mergers)", "grezzo": "Elenco-comuni-soppressi.zip"},
}
PAGINA_ISTAT = "https://demo.istat.it/app/?i=POS"

# valore + fonte + frammento (testo normalizzato: spazi compattati, apostrofi e virgolette dritti)
LETTURE = {
    "vigore": {"valore": ["2026-04-07", "2026-12-31"], "fonte": "art24ter", "frammento": "Testo in vigore dal: 7-4-2026 al: 31-12-2026"},
    "regioni": {"valore": ["Sicilia", "Calabria", "Sardegna", "Campania", "Basilicata", "Abruzzo", "Molise", "Puglia"], "fonte": "art24ter",
                "frammento": "in uno dei comuni appartenenti al territorio delle regioni Sicilia, Calabria, Sardegna, Campania, Basilicata, Abruzzo, Molise e Puglia"},
    "sisma2016": {"valore": True, "fonte": "art24ter", "frammento": "o in uno dei comuni di cui agli allegati 1, 2 e 2-bis al decreto-legge 17 ottobre 2016, n. 189"},
    "sisma2009": {"valore": True, "fonte": "art24ter", "frammento": "o in uno dei comuni interessati dagli eventi sismici del 6 aprile 2009"},
    "soglia": {"valore": 30000, "fonte": "art24ter", "frammento": "avente comunque una popolazione non superiore a ((30.000 abitanti))"},
    "pensione": {"valore": True, "fonte": "art24ter", "frammento": "titolari dei redditi da pensione di cui all'articolo 49, comma 2, lettera a), erogati da soggetti esteri"},
    "aliquota": {"valore": 7, "fonte": "art24ter", "frammento": "possono optare per l'assoggettamento dei redditi di qualunque categoria, prodotti all'estero"},
    "aliquota_7": {"valore": 7, "fonte": "art24ter", "frammento": "con aliquota del 7 per cento per ciascuno dei periodi di imposta di validità dell'opzione"},
    "cinque_anni": {"valore": 5, "fonte": "art24ter", "frammento": "che non siano state fiscalmente residenti in Italia ai sensi dell'articolo 2, comma 2, nei cinque periodi d'imposta precedenti"},
    "accordi": {"valore": True, "fonte": "art24ter", "frammento": "trasferiscono la residenza da Paesi con i quali sono in vigore accordi di cooperazione amministrativa"},
    "nove_anni": {"valore": 9, "fonte": "art24ter", "frammento": "è valida per i primi nove periodi d'imposta successivi a quello in cui diviene efficace"},
    "dichiarazione": {"valore": True, "fonte": "art24ter", "frammento": "è esercitata nella dichiarazione dei redditi relativa al periodo d'imposta in cui viene trasferita la residenza in Italia"},
    "versamento": {"valore": True, "fonte": "art24ter", "frammento": "L'imposta è versata in unica soluzione entro il termine previsto per il versamento del saldo delle imposte sui redditi"},
    "revoca": {"valore": True, "fonte": "art24ter", "frammento": "La revoca o la decadenza dal regime precludono l'esercizio di una nuova opzione"},
    "esclusione_stati": {"valore": True, "fonte": "art24ter", "frammento": "possono manifestare la facoltà di non avvalersi dell'applicazione dell'imposta sostitutiva con riferimento ai redditi prodotti in uno o più Stati"},
    "abrogato_2027": {"valore": "2027-01-01", "fonte": "art24ter_2027", "frammento": "PROVVEDIMENTO ABROGATO DAL D.LGS. 19 GIUGNO 2026, N. 117"},
    "l34": {"valore": "2026-03-11", "fonte": "l34", "frammento": "le parole: «20.000 abitanti» sono sostituite dalle seguenti: «30.000 abitanti»"},
    "l34_vigore": {"valore": "2026-04-07", "fonte": "l34", "frammento": "Testo in vigore dal: 7-4-2026"},
    "art247": {"valore": 30000, "fonte": "art247", "frammento": "avente comunque una popolazione non superiore a ((30.000 abitanti))"},
    "art247_titolo": {"valore": True, "fonte": "art247", "frammento": "Imposizione sostitutiva sui redditi da pensione di fonte estera dei soggetti che trasferiscono la residenza in Italia"},
    "art247_vigore": {"valore": "2026-08-07", "fonte": "art247", "frammento": "Testo in vigore dal: 7-8-2026"},
    "art247_nove": {"valore": 9, "fonte": "art247", "frammento": "è valida per i primi nove periodi d'imposta successivi a quello in cui diviene efficace"},
    "decorrenza_2027": {"valore": "2027-01-01", "fonte": "art377", "frammento": "Le disposizioni del presente testo unico si applicano a decorrere dal 1° gennaio 2027"},
    "ade_aggiornata": {"valore": "2026-05-08", "fonte": "ade", "frammento": "Ultimo aggiornamento: 8 maggio 2026"},
    "ade_30mila": {"valore": "2026-04-07", "fonte": "ade", "frammento": "con popolazione non superiore a 30mila abitanti (tale limite è in vigore dal 7 aprile 2026, in precedenza era 20mila abitanti)"},
    "ade_sisma": {"valore": True, "fonte": "ade", "frammento": "sempre con non più di 30mila abitanti, interessati dagli eventi sismici del 6 aprile 2009"},
    "ade_anno": {"valore": True, "fonte": "ade", "frammento": "riferito al 1° gennaio dell'anno precedente il primo periodo di validità dell'opzione"},
    "ade_istat": {"valore": True, "fonte": "ade", "frammento": "si considera il dato risultante dalla \"Rilevazione comunale annuale del movimento e calcolo della popolazione\" pubblicata sul sito dell'Istat"},
    "ade_durata_dato": {"valore": True, "fonte": "ade", "frammento": "Tale dato rileva per tutta la durata di validità dell'opzione, sempre che il contribuente non trasferisca la residenza in altro comune"},
    "ade_altro_comune": {"valore": True, "fonte": "ade", "frammento": "per il quale va considerato il dato della popolazione risultante al 1° gennaio dell'anno antecedente a quello di trasferimento della residenza"},
    "ade_nove": {"valore": 9, "fonte": "ade", "frammento": "per ciascuno dei nove periodi d'imposta di validità dell'opzione"},
    "circ_anno": {"valore": True, "fonte": "circ21e", "frammento": "di Statistica (ISTAT), riferito al 1° gennaio dell'anno precedente a quello in cui"},
    "circ_dieci": {"valore": 10, "fonte": "circ21e", "frammento": "la validità massima del regime è pari a dieci anni"},
    "circ_esempio": {"valore": True, "fonte": "circ21e", "frammento": "potrà beneficiare dell'imposizione sostitutiva a partire da tale annualità e fino al 2028 (incluso), senza possibilità di rinnovare l'opzione alla scadenza"},
    "circ_accordi": {"valore": True, "fonte": "circ21e", "frammento": "accordo di cooperazione amministrativa (cioè uno strumento che consente lo scambio di informazioni in materia fiscale"},
    "bura_titolo": {"valore": True, "fonte": "bura2009", "frammento": "ELENCO DEI COMUNI NELL'AREA CRATERE Comuni di cui al Decreto del Commissario Delegato n. 3 del 16 Aprile 2009"},
    "istat2025": {"valore": "2025-01-01", "fonte": "istat2025", "frammento": "Popolazione residente per età, sesso e stato civile al 1° gennaio 2025"},
    "istat2026": {"valore": "2026-01-01", "fonte": "istat2026", "frammento": "Popolazione residente per età e sesso al 1° gennaio 2026 (stima)"},
}

# nomi degli allegati scritti diversamente dall'elenco ISTAT (nome nell'allegato, sigla) -> codice ISTAT
ALIAS = {("Monsapietro Morico", "FM"): "109012", ("Monteleone", "FM"): "109019", ("Serravalle del Chienti", "MC"): "043052",
         ("Isola del Gran Sasso", "TE"): "067026"}
# Comuni degli allegati poi fusi (elenco ISTAT dei soppressi, 1/1/2017): nome -> codice del Comune di oggi
FUSIONI = {"Acquacanina": "043017", "Fiordimonte": "043058", "Pievebovigliana": "043058"}
# elenco 2009 (BURA 2017) con un nome cambiato dopo: Popoli -> Popoli Terme (L.R. Abruzzo 10/7/2023 n. 32, dal 13/7/2023; elenco ISTAT
# delle variazioni amministrative dal 1991)
ALIAS_2009 = {"Popoli": "068033"}

GL = ["us", "gb"]
QUERY = ["italy 7 tax", "italy 7 flat tax", "italy 7 percent tax", "italy flat tax pensioners", "7 tax towns", "italy 7 tax towns",
         "italy 7 tax regime", "italy 7 tax rule", "italy 7 tax map", "italy 7 percent tax pension", "italy retirement 7 tax",
         "italy 7 tax requirements", "italy 7 tax population", "italy 7 tax 30000", "italy 7 tax earthquake", "italy 7 tax us citizens"]


def norm(t):
    t = H.unescape(t).replace(" ", " ").replace(" ", " ").replace("­", "")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"(?:\s*\.){4,}", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def chiave(s):
    """Nome di Comune senza accenti, apostrofi, spazi e maiuscole (per confrontare allegati ed elenco ISTAT)."""
    s = unicodedata.normalize("NFKD", s.replace("’", "'")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


def scarica(u, opener=None):
    try:
        r = (opener.open if opener else urllib.request.urlopen)(urllib.request.Request(u, headers=UA), timeout=180)
        return r.status, r.read(), r.headers.get("Last-Modified", "")
    except Exception as e:  # noqa: BLE001
        return getattr(e, "code", 0) or 0, b"", ""


def testo_di(b):
    if b[:4] == b"%PDF":
        return norm(subprocess.run(["pdftotext", "-", "-"], input=b, capture_output=True).stdout.decode("utf-8", "replace")), "pdf"
    s = b.decode("utf-8", "replace")
    s = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", s)
    return norm(re.sub(r"<[^>]+>", " ", s)), "html"


def leggi(f):
    """-> (meta, testo, byte). Articoli del D.Lgs. 117 e allegati del D.L. 189: prima il cookie della pagina dell'atto."""
    opener = None
    if f.get("cookie"):
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        scarica(f["link"], opener)
    st, b, lm = scarica(f["url"], opener)
    meta = {"url": f["url"], "http": st}
    if st != 200 or not b:
        return meta, "", b""
    meta["last_modified"] = lm
    meta["sha256"] = hashlib.sha256(b).hexdigest()
    meta["byte"] = len(b)
    if f.get("grezzo"):
        GREZZI.mkdir(parents=True, exist_ok=True)
        (GREZZI / f["grezzo"]).write_bytes(b)
        return meta, "", b
    t, tipo = testo_di(b)
    meta["formato"] = tipo
    meta["sha256"] = hashlib.sha256(t.encode("utf-8")).hexdigest()
    return meta, t, b


def popolazione(b):
    """POSAS zip -> (intestazione, {codice: totale}) dalla riga Età = 999 (totale del Comune)."""
    z = zipfile.ZipFile(io.BytesIO(b))
    nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
    righe = z.read(nome).decode("utf-8-sig").splitlines()
    out = {}
    for r in csv.reader(righe[2:], delimiter=";"):
        if len(r) > 3 and r[2] == "999":
            out[r[0]] = int(r[-1])
    return norm(righe[0].strip('"')), out


def elenco_comuni(b):
    r = list(csv.reader(io.StringIO(b.decode("cp1252")), delimiter=";"))
    h = r[0]
    i = {k: h.index(k) for k in ("Codice Comune formato alfanumerico", "Denominazione in italiano", "Denominazione altra lingua",
                                  "Denominazione Regione", "Sigla automobilistica")}
    return [{"codice": x[i["Codice Comune formato alfanumerico"]], "nome": x[i["Denominazione in italiano"]],
             "altro": x[i["Denominazione altra lingua"]], "regione": x[i["Denominazione Regione"]], "sigla": x[i["Sigla automobilistica"]]}
            for x in r[1:] if len(x) > 14 and x[0]]


def soppressi(b):
    z = zipfile.ZipFile(io.BytesIO(b))
    nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
    righe = list(csv.reader(io.StringIO(z.read(nome).decode("cp1252")), delimiter=";"))
    return {r[4]: {"anno": r[0], "data": r[6], "codice_nuovo": r[7], "nome_nuovo": r[8]} for r in righe[1:] if len(r) > 8}


def nomi_allegato(t):
    """Testo dell'allegato -> [(numero, nome, sigla o '', regione)]."""
    corpo = re.split(r"\((?:Art\.|articolo) 1\)", t, maxsplit=1)[-1].split("articolo precedente", 1)[0]
    out, reg = [], ""
    for m in re.finditer(r"(?:REGIONE|Regione) ([A-Z][A-Za-z]+)|(\d+)[.)] ([^;.:()]+?)(?: \(([A-Z]{2})\))?(?=\s*[;.)]|\s*\)\))", corpo):
        if m.group(1):
            reg = m.group(1).capitalize()
            continue
        out.append((int(m.group(2)), m.group(3).strip(), m.group(4) or "", reg))
    return out


def nomi_bura(t):
    """Allegato B1 della Regione Abruzzo -> [(provincia, nome)]."""
    corpo = t.split("successivi atti di recepimento e attuazione.", 1)[-1]
    out = []
    for m in re.finditer(r"Provincia (?:de L'Aquila|di Teramo|di Pescara)(.*?)(?=Provincia d|$)", corpo):
        prov = m.group(0).split(" ", 2)[1] + " " + m.group(0).split(" ", 3)[2]
        for n in m.group(1).split(","):
            n = n.strip()
            if n:
                out.append((prov, n))
    return out


def autocompleta(q, gl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": "en", "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda():
    out = {}
    for q in QUERY:
        for gl in GL:
            out[f"{gl}|{q}"] = autocompleta(q, gl)
            time.sleep(0.25)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl={us,gb}&hl=en&q=…",
            "query": out}


def main():
    oggi = date.today().isoformat()
    errori = []
    fonti, testi, grezzi = {}, {}, {}
    for k, f in FONTI.items():
        meta, t, b = leggi(f)
        if meta["http"] != 200:
            errori.append(f"fonte {k}: non leggibile (HTTP {meta['http']}): {f['url']}")
        meta.update({kk: f[kk] for kk in ("editore", "titolo", "link", "data") if kk in f})
        meta["letto_il"] = oggi
        fonti[k], testi[k], grezzi[k] = meta, t, b
    # ISTAT: popolazione 2025 e 2026, elenco dei Comuni, soppressi
    pop = {}
    for anno in ("2025", "2026"):
        if grezzi.get(f"istat{anno}"):
            intest, pop[anno] = popolazione(grezzi[f"istat{anno}"])
            testi[f"istat{anno}"] = intest
            fonti[f"istat{anno}"]["intestazione"] = intest
    el = elenco_comuni(grezzi["elenco"]) if grezzi.get("elenco") else []
    sop = soppressi(grezzi["soppressi"]) if grezzi.get("soppressi") else {}
    for k, v in LETTURE.items():
        if v["frammento"] not in testi.get(v["fonte"], ""):
            errori.append(f"{k}: frammento non trovato in {v['fonte']}: {v['frammento'][:110]!r}")
    codici = {c["codice"] for c in el}
    if not el or set(pop.get("2025", {})) != codici or set(pop.get("2026", {})) != codici:
        errori.append(f"ISTAT: codici diversi tra elenco ({len(codici)}), 2025 ({len(pop.get('2025', {}))}) e 2026 ({len(pop.get('2026', {}))})")
    regioni8 = LETTURE["regioni"]["valore"]
    if any(r not in {c["regione"] for c in el} for r in regioni8):
        errori.append("ISTAT: una delle 8 regioni della legge non è nell'elenco")
    # allegati del D.L. 189/2016
    per_chiave = {}
    for c in el:
        per_chiave.setdefault(chiave(c["nome"]), []).append(c)
    per_codice = {c["codice"]: c for c in el}
    sisma = []
    attesi = {"all1": 62, "all2": 69, "all2bis": 9}
    for k, n_att in attesi.items():
        voci = nomi_allegato(testi.get(k, ""))
        if [v[0] for v in voci] != list(range(1, n_att + 1)):
            errori.append(f"{k}: numerazione letta diversa da 1..{n_att} ({len(voci)} nomi)")
        for num, nome, sigla, reg in voci:
            codice, nota = None, ""
            if (nome, sigla) in ALIAS:
                codice, nota = ALIAS[(nome, sigla)], "nome scritto diversamente nell'allegato"
            elif nome in FUSIONI:
                s = sop.get(nome)
                if not s or s["codice_nuovo"] != FUSIONI[nome]:
                    errori.append(f"{k}: fusione di {nome} non confermata dall'elenco ISTAT dei soppressi")
                codice, nota = FUSIONI[nome], f"fuso il {s['data'] if s else '?'} in {s['nome_nuovo'] if s else '?'}"
            else:
                cand = [c for c in per_chiave.get(chiave(nome), []) if (c["sigla"] == sigla if sigla else c["regione"] == reg)]
                if len(cand) == 1:
                    codice = cand[0]["codice"]
            if not codice or codice not in per_codice:
                errori.append(f"{k}: {num}. {nome} ({sigla}) non trovato nell'elenco ISTAT")
                continue
            if per_codice[codice]["regione"] != reg:
                errori.append(f"{k}: {nome} è in {per_codice[codice]['regione']}, l'allegato dice {reg}")
            sisma.append({"allegato": k, "n": num, "nome": nome, "sigla": sigla, "regione": reg, "codice": codice, "nota": nota})
    # sisma 2009 (Regione Abruzzo): tutti in Abruzzo
    s2009 = []
    for prov, nome in nomi_bura(testi.get("bura2009", "")):
        cand = [c for c in per_chiave.get(chiave(nome), []) if c["regione"] == "Abruzzo"]
        if nome in ALIAS_2009:
            cand = [per_codice[ALIAS_2009[nome]]]
        if len(cand) != 1:
            errori.append(f"sisma 2009: {nome} ({prov}) non trovato tra i Comuni dell'Abruzzo")
            continue
        s2009.append({"nome": nome, "provincia": prov, "codice": cand[0]["codice"]})
    if len(s2009) != 57:
        errori.append(f"sisma 2009: {len(s2009)} Comuni letti (attesi 57)")
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom:
        errori.append("domanda: nessun dato di autocompletamento (lanciare con --domanda)")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    # righe compatte: [codice, nome, altro nome, sigla, regione, pop 1/1/2025, pop 1/1/2026]
    comuni = [[c["codice"], c["nome"], c["altro"], c["sigla"], c["regione"], pop["2025"][c["codice"]], pop["2026"][c["codice"]]]
              for c in sorted(el, key=lambda c: c["codice"])]
    letture = {k: {"valore": v["valore"], "fonte": v["fonte"], "frammento": v["frammento"]} for k, v in LETTURE.items()}
    contenuto = {"letture": letture, "fonti": fonti, "sisma2016": sisma, "sisma2009": s2009, "comuni": comuni,
                 "anni_popolazione": {"2025": {"riferimento": "2025-01-01", "trasferimento": "2026", "stima": False},
                                      "2026": {"riferimento": "2026-01-01", "trasferimento": "2027", "stima": True}},
                 "pagina_istat": PAGINA_ISTAT}
    uscita = {"_nota": "Generato da raccolta/flat7.py: non modificare a mano (le regole lette a mano stanno in LETTURE dentro lo script). "
                       "Fonti: Normattiva, Agenzia delle Entrate, Regione Abruzzo, ISTAT. Righe di 'comuni': codice, nome, altro nome, sigla, regione, "
                       "popolazione al 1/1/2025, popolazione al 1/1/2026 (stima).",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0, separators=(",", ":")) + "\n", encoding="utf-8")
    soglia = LETTURE["soglia"]["valore"]
    n8 = [c for c in comuni if c[4] in regioni8]
    fuori = {c["codice"] for c in sisma if c["regione"] not in regioni8}
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(letture)} regole, {len(comuni)} Comuni ISTAT; 8 regioni: {len(n8)} Comuni, "
          f"entro {soglia} {sum(c[5] <= soglia for c in n8)} (1/1/2025) e {sum(c[6] <= soglia for c in n8)} (1/1/2026); "
          f"allegati sisma 2016-2017: {len(sisma)} nomi, {len(fuori)} Comuni fuori dalle 8 regioni; sisma 2009: {len(s2009)} (tutti in Abruzzo); "
          f"impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
